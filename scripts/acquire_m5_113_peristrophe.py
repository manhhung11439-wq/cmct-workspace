import pathlib,requests,time,hashlib,json,re
import fitz
OUT=pathlib.Path("evidence/m5_t1_113_peristrophe_2016"); OUT.mkdir(parents=True,exist_ok=True)
URLS=["https://pdfs.semanticscholar.org/4ae1/b7454ee1e6e9b34b24570ae371b6d682e98d.pdf","https://www.scipress.com/IJPPE.4.14.pdf"]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/31.2 Peristrophe bivalvis CC-BY figure acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
r=get(URL); b=r.content
if b[:4]!=b"%PDF": raise RuntimeError("Not PDF "+r.url+" "+str(r.headers.get("content-type")))
pdf=OUT/"article.pdf"; pdf.write_bytes(b)
doc=fitz.open(stream=b,filetype="pdf")
pages=[]; extracted=[]
for i,p in enumerate(doc):
    txt=p.get_text("text")
    pages.append({"number":i+1,"text":txt[:6000],"images":len(p.get_images(full=True))})
    pix=p.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False)
    pix.save(OUT/f"page_{i+1:02d}_preview.png")
    for j,img in enumerate(p.get_images(full=True),1):
        xref=img[0]
        try:
            info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
        except Exception: continue
        if info.get("width",0)<250 or info.get("height",0)<180: continue
        pth=OUT/f"p{i+1:02d}_img{j:02d}.{ext}"; pth.write_bytes(data)
        s1,s256=hh(data)
        extracted.append({"page":i+1,"xref":xref,"file":str(pth),"width":info.get("width"),"height":info.get("height"),"bytes":len(data),"sha1":s1,"sha256":s256})
man={"id":113,"target":"Lá Cẩm / Peristrophe bivalvis (L.) Merr.","article":"Nguyen Van Quan et al. 2016, IJPPE 4:14-26",
"doi":"10.18052/www.scipress.com/IJPPE.4.14","license":"CC BY 4.0","source_url":r.url,
"pdf_bytes":len(b),"pdf_sha1":hh(b)[0],"pdf_sha256":hh(b)[1],"pdf_pages":len(doc),
"pages":pages,"extracted_images":extracted,
"controller_status":"PDF/images acquired; visual role must be locked before promotion"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"pdf":r.url,"bytes":len(b),"pages":len(doc),"images":extracted},ensure_ascii=False),flush=True)
