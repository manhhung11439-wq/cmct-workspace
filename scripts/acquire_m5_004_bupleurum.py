# CMCT T1 M5 #4 Bupleurum chinense dried root figure acquisition
import io,json,hashlib,pathlib,time,re
import requests,fitz
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_004_bupleurum"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.0 Bupleurum chinense exact dried-root figure extraction"

def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()

def hh(data): return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()

pdf_urls=[
 "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5448051/fullTextPDF",
 "https://downloads.hindawi.com/journals/bmri/2017/7597596.pdf"
]
r=None
for u in pdf_urls:
    try:
        rr=get(u)
        if rr.content.startswith(b"%PDF"):
            r=rr; break
    except Exception as e:
        print("PDF_SOURCE_FAIL",u,repr(e),flush=True)
if r is None: raise RuntimeError("no PDF source succeeded")
pdf=r.content
if not pdf.startswith(b"%PDF"): raise RuntimeError("not PDF")
pp=OUT/"m5_004_article_original.pdf"; pp.write_bytes(pdf)
ps1,ps256=hh(pdf)
doc=fitz.open(stream=pdf,filetype="pdf")
page_idx=None; page_text=""
for i,p in enumerate(doc):
    txt=p.get_text("text")
    low=" ".join(txt.lower().split())
    if "the whole plant of bupleurum chinense" in low and "roots of bupleurum chinense" in low:
        page_idx=i; page_text=txt; break
if page_idx is None: raise RuntimeError("Figure 1 page not found")
page=doc[page_idx]
pix=page.get_pixmap(matrix=fitz.Matrix(2.2,2.2),alpha=False)
pagepng=OUT/f"m5_004_fig1_page_{page_idx+1}.png"; pix.save(str(pagepng))

imgs=[]
for k,img in enumerate(page.get_images(full=True),1):
    xref=img[0]; ex=doc.extract_image(xref); data=ex["image"]
    if len(data)<15000: continue
    try:
        im=Image.open(io.BytesIO(data)); w,h=im.size; fmt=im.format
    except Exception: continue
    p=OUT/f"m5_004_fig1_xref{xref}_{k}.{ex['ext']}"; p.write_bytes(data)
    s1,s256=hh(data)
    imgs.append({"xref":xref,"file":str(p),"bytes":len(data),"width":w,"height":h,"format":fmt,"sha1":s1,"sha256":s256})

# Save a contact-sheet of extracted candidate images for controller review.
thumbs=[]
for x in imgs:
    im=Image.open(x["file"]).convert("RGB")
    im.thumbnail((700,500))
    thumbs.append((x["xref"],im.copy()))
if thumbs:
    W=max(im.width for _,im in thumbs); H=sum(im.height+40 for _,im in thumbs)
    sheet=Image.new("RGB",(W,H),"white"); y=0
    from PIL import ImageDraw
    dr=ImageDraw.Draw(sheet)
    for xref,im in thumbs:
        dr.text((5,y+5),f"xref {xref}  {im.width}x{im.height}",fill="black")
        y+=30; sheet.paste(im,(0,y)); y+=im.height+10
    sheet.save(OUT/"m5_004_extracted_contact_sheet.png")

manifest={
 "id":4,
 "article":"Yang F et al. BioMed Research International 2017;2017:7597596",
 "doi":"10.1155/2017/7597596",
 "license":"CC BY",
 "figure_caption":"The whole plant of Bupleurum chinense DC. (A); whole plant of B. scorzonerifolium (B); roots of B. chinense (C); roots of B. scorzonerifolium (D).",
 "material_context":"Article states Radix Bupleuri is derived from dried roots of Bupleurum chinense and B. scorzonerifolium; collected, aerial parts/soil removed, and dried.",
 "resolved_pdf_url":r.url,
 "pdf_file":str(pp),"pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,
 "figure_page":page_idx+1,"page_text_excerpt":page_text[:6000],"images":imgs
}
(OUT/"extract_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_004_PAGE",page_idx+1,flush=True)
print("M5_004_IMAGES="+json.dumps(imgs,ensure_ascii=False),flush=True)
print("M5_004_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
