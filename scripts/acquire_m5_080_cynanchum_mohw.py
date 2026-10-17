import pathlib,requests,time,hashlib,json
import fitz
OUT=pathlib.Path("evidence/m5_t1_080_cynanchum_mohw"); OUT.mkdir(parents=True,exist_ok=True)
PDF_URL="https://www.mohw.gov.tw/dl-28815-0d94376a-e8c6-4deb-973d-0ad8e15fff93.html"
LICENSE_URL="https://www.mohw.gov.tw/fp-185-9466-2.html"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/32.0 MOHW Cynanchum atratum crude-drug acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
r=get(PDF_URL); pb=r.content
if not pb.startswith(b"%PDF"): raise RuntimeError(f"Not PDF: {r.status_code} {r.url} {r.headers.get('content-type')} {pb[:80]!r}")
pdf=OUT/"mohw_report.pdf"; pdf.write_bytes(pb); ps1,ps256=hh(pb)
lic=get(LICENSE_URL); (OUT/"license_page.html").write_bytes(lic.content); ls1,ls256=hh(lic.content)
doc=fitz.open(stream=pb,filetype="pdf")
renders=[]
for idx in [28,29]:
    if idx>=len(doc): continue
    p=doc[idx]
    pix=p.get_pixmap(matrix=fitz.Matrix(3.5,3.5),alpha=False)
    out=OUT/f"page_{idx+1}_3p5x.png"; pix.save(out)
    renders.append({"page_index":idx,"page_number":idx+1,"file":str(out),"width":pix.width,"height":pix.height})
# extract all page 29/30 images
embedded=[]
for idx in [28,29]:
    if idx>=len(doc): continue
    p=doc[idx]
    for j,img in enumerate(p.get_images(full=True),1):
        xref=img[0]
        try:
            info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
        except: continue
        fn=OUT/f"p{idx+1}_image_{j}.{ext}"; fn.write_bytes(data)
        s1,s256=hh(data)
        embedded.append({"page_number":idx+1,"xref":xref,"file":str(fn),"ext":ext,"width":info.get("width"),"height":info.get("height"),"bytes":len(data),"sha1":s1,"sha256":s256})
man={
 "id":80,"target":"Bạch Vi / Cynanchum atratum Bunge / dried root and rhizome",
 "source_url":PDF_URL,"resolved_pdf_url":r.url,"pdf_bytes":len(pb),"pdf_sha1":ps1,"pdf_sha256":ps256,"pdf_pages":len(doc),
 "license_url":LICENSE_URL,"license_statement":"MOHW website materials are provided under Open Government Data License, version 1.0, subject to stated exceptions and attribution.","license_page_sha1":ls1,"license_page_sha256":ls256,
 "source_text_lock":"Report text identifies 白薇 Cynanchum atratum BUNGE. source as dried root and rhizome and describes the crude drug; Figure 10 is Cynanchum atratum.",
 "renders":renders,"embedded_images":embedded,
 "controller_status":"SOURCE+LICENSE+BYTES ACQUIRED; VISUAL FIGURE-10 LOCK REQUIRED BEFORE CROP/PROMOTION"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
