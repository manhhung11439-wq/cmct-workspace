import pathlib,requests,time,hashlib,json
import fitz
OUT=pathlib.Path("evidence/m5_t1_045_pcc_pdf_hires"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC8048166"; DOI="10.1186/s12951-021-00847-y"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/28.2 PCC PDF high-resolution acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
candidates=[
 f"https://link.springer.com/content/pdf/{DOI}.pdf",
 f"https://link.springer.com/article/{DOI}.pdf",
 f"https://pmc.ncbi.nlm.nih.gov/articles/{PMC}/pdf/",
]
pb=None; pdf_url=None; attempts=[]
for u in candidates:
    try:
        r=get(u); ct=(r.headers.get("content-type") or "").lower()
        attempts.append({"url":u,"final":r.url,"status":r.status_code,"content_type":ct,"bytes":len(r.content)})
        if r.content[:4]==b"%PDF" or "application/pdf" in ct:
            pb=r.content; pdf_url=r.url; break
    except Exception as e: attempts.append({"url":u,"error":repr(e)})
if pb is None: raise RuntimeError("No PDF acquired: "+json.dumps(attempts))
pdf=OUT/"article.pdf"; pdf.write_bytes(pb)
ps1,ps256=hh(pb); doc=fitz.open(stream=pb,filetype="pdf")
pages=[]
for i,p in enumerate(doc):
    txt=p.get_text("text")
    rec={"index":i,"number":i+1,"text_head":txt[:1800],"images":len(p.get_images(full=True))}
    pages.append(rec)
    if i<8:
        pix=p.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False)
        pix.save(OUT/f"page_{i+1}_preview.png")
# candidate pages scored by keywords + image count
keys=["Phellodendri","PCC","calcination","Illustration","carbon dots"]
scores=[]
for rec in pages:
    score=sum(3 for k in keys if k.lower() in rec["text_head"].lower())+rec["images"]
    scores.append((score,rec["index"]))
scores.sort(reverse=True)
target_page=scores[0][1] if scores else 0
page=doc[target_page]
pix=page.get_pixmap(matrix=fitz.Matrix(4,4),alpha=False); pix.save(OUT/f"candidate_page_{target_page+1}_4x.png")
extracted=[]
for j,img in enumerate(page.get_images(full=True),1):
    xref=img[0]
    try:
        info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
    except Exception:
        continue
    pth=OUT/f"candidate_page_image_{j}.{ext}"; pth.write_bytes(data)
    s1,s256=hh(data)
    extracted.append({"xref":xref,"file":str(pth),"ext":ext,"width":info.get("width"),"height":info.get("height"),"bytes":len(data),"sha1":s1,"sha256":s256})
man={"id":45,"pmc":PMC,"doi":DOI,"attempts":attempts,"pdf_url":pdf_url,"pdf_bytes":len(pb),"pdf_sha1":ps1,"pdf_sha256":ps256,
     "pdf_pages":len(doc),"pages":pages,"candidate_page_index":target_page,"candidate_page_number":target_page+1,
     "candidate_page_images":extracted,
     "controller_status":"PDF acquired and preview pages exported; visual lock required"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST_SUMMARY="+json.dumps({"pdf_url":pdf_url,"pages":len(doc),"scores":scores[:8],"candidate_page":target_page+1,"images":extracted},ensure_ascii=False),flush=True)
