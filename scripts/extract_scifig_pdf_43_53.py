# CMCT T1 exact scientific figure extraction from original article PDFs — #43/#53
import io,re,json,hashlib,pathlib,time
import requests, fitz
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_scifig_pdf_extract_43_53"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/2.7 exact article PDF figure extraction"
def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True);last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i)));continue
        r.raise_for_status();return r
    last.raise_for_status()
def hh(data):
    return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()

jobs=[
 {"id":53,"pdf":"https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2021.685575/pdf",
  "needle":["A photograph of the dried root","Isatis indigotica"],"license":"CC BY",
  "citation":"Nie et al. 2021, Frontiers in Pharmacology 12:685575"},
 {"id":43,"pdf":"https://link.springer.com/content/pdf/10.1007/s11434-016-1136-5.pdf",
  "needle":["The medicinal plant Scutellaria baicalensis","dried root"],"license":"CC BY 4.0",
  "citation":"Zhao, Chen & Martin 2016, Science Bulletin 61:1391–1398"},
]
manifest=[]
for job in jobs:
    r=get(job["pdf"]); pdfdata=r.content
    if not pdfdata.startswith(b"%PDF"): raise RuntimeError(f"#{job['id']} not PDF: {r.url} {r.headers.get('content-type')}")
    ppdf=OUT/f"m5_{job['id']:03d}_article_original.pdf";ppdf.write_bytes(pdfdata)
    s1,s256=hh(pdfdata)
    doc=fitz.open(stream=pdfdata,filetype="pdf")
    page_idx=None
    page_text=""
    for i,p in enumerate(doc):
        txt=p.get_text("text")
        if all(n.lower() in txt.lower() for n in job["needle"]):
            page_idx=i;page_text=txt;break
    if page_idx is None:
        # broader fallback
        for i,p in enumerate(doc):
            txt=p.get_text("text")
            if "Fig. 1" in txt or "FIGURE 1" in txt:
                if any(n.lower() in txt.lower() for n in job["needle"]):
                    page_idx=i;page_text=txt;break
    if page_idx is None: raise RuntimeError(f"#{job['id']} caption page not found")
    page=doc[page_idx]
    # render full page for visual provenance/debug
    pix=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False)
    page_png=OUT/f"m5_{job['id']:03d}_figure_page_{page_idx+1}.png";pix.save(str(page_png))
    extracted=[]
    for k,img in enumerate(page.get_images(full=True),1):
        xref=img[0]
        ex=doc.extract_image(xref)
        data=ex["image"];ext=ex["ext"]
        if len(data)<5000: continue
        pi=OUT/f"m5_{job['id']:03d}_p{page_idx+1}_xref{xref}_{k}.{ext}"
        pi.write_bytes(data)
        try:
            with Image.open(io.BytesIO(data)) as im:w,h=im.size
        except Exception:
            w=h=None
        a,b=hh(data)
        extracted.append({"file":str(pi),"bytes":len(data),"width":w,"height":h,"ext":ext,"xref":xref,"sha1":a,"sha256":b})
    manifest.append({"id":job["id"],"resolved_pdf_url":r.url,"pdf_file":str(ppdf),"pdf_bytes":len(pdfdata),
      "pdf_sha1":s1,"pdf_sha256":s256,"license":job["license"],"citation":job["citation"],
      "figure_page":page_idx+1,"page_text_excerpt":page_text[:3000],"extracted_images":extracted})
    print("SCI_PDF",job["id"],"PAGE",page_idx+1,"IMAGES",[(x["bytes"],x["width"],x["height"],x["file"]) for x in extracted],flush=True)
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("CMCT_SCI_PDF_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
