import pathlib,requests,time,hashlib,json
import fitz
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_125_scoparia_jbpr2023"); OUT.mkdir(parents=True,exist_ok=True)
URLS=[
 "https://www.jbpr.in/index.php/jbpr/article/view/956/827",
 "https://www.jbpr.in/index.php/jbpr/article/download/956/827"
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/33.0 Scoparia dulcis pharmacognosy acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        return r
    return last
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
pb=None; src=None; attempts=[]
for u in URLS:
    r=get(u); ct=(r.headers.get("content-type") or "").lower()
    attempts.append({"url":u,"status":r.status_code,"final":r.url,"content_type":ct,"bytes":len(r.content)})
    if r.ok and (r.content[:4]==b"%PDF" or "application/pdf" in ct):
        pb=r.content; src=r.url; break
if pb is None: raise RuntimeError("PDF unavailable: "+json.dumps(attempts))
pdf=OUT/"article.pdf"; pdf.write_bytes(pb); s1,s256=hh(pb)
doc=fitz.open(stream=pb,filetype="pdf")
pages=[]; imgs=[]
for i,p in enumerate(doc):
    txt=p.get_text("text")
    pages.append({"page":i+1,"text_head":txt[:2500],"images":len(p.get_images(full=True))})
    pix=p.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False); pix.save(OUT/f"page_{i+1:02d}.png")
    for j,img in enumerate(p.get_images(full=True),1):
        xref=img[0]
        try:
            info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
        except: continue
        if info.get("width",0)<180 or info.get("height",0)<120: continue
        pth=OUT/f"p{i+1:02d}_img{j:02d}.{ext}"; pth.write_bytes(data)
        h1,h256=hh(data)
        imgs.append({"page":i+1,"xref":xref,"file":str(pth),"width":info.get("width"),"height":info.get("height"),"ext":ext,"bytes":len(data),"sha1":h1,"sha256":h256})
man={"id":125,"target":"Cam Thảo Đất / Scoparia dulcis L. / whole plant medicinal material",
     "article":"Sharma A., Singh Saluja M., Jain P. 2023. Pharmacognostical Analysis and In Vitro Antioxidant Activity of Scoparia dulcis L.",
     "doi":"10.32553/jbpr.v12i1.956","license":"CC BY 4.0","source_url":src,
     "pdf_bytes":len(pb),"pdf_sha1":s1,"pdf_sha256":s256,"pdf_pages":len(doc),
     "attempts":attempts,"pages":pages,"images":imgs,
     "controller_status":"PDF/embedded images acquired; actual medicinal-material image requires visual lock"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST_SUMMARY="+json.dumps({"attempts":attempts,"pdf_pages":len(doc),"images":imgs},ensure_ascii=False),flush=True)
