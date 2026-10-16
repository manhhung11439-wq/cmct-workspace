# CMCT T1 M5 #57 exact shade-dried Artemisia annua herbal drug from MDPI Fig 1b
import io,json,hashlib,pathlib,time
import requests,fitz
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_057_artemisia_mdpi");OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/3.2 exact Artemisia annua herbal-drug figure extraction"
def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True);last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i)));continue
        r.raise_for_status();return r
    last.raise_for_status()
def hh(data):return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()

pdf_url="https://www.mdpi.com/1999-4923/17/7/890/pdf"
r=get(pdf_url);pdf=r.content
if not pdf.startswith(b"%PDF"):raise RuntimeError("not PDF")
pp=OUT/"m5_057_mdpi_article_original.pdf";pp.write_bytes(pdf);ps1,ps256=hh(pdf)
doc=fitz.open(stream=pdf,filetype="pdf")
page_idx=None;page_text=""
for i,p in enumerate(doc):
    txt=p.get_text("text")
    low=" ".join(txt.lower().split())
    if ("plant material" in low and "artemisia annua" in low and ("figure 1" in low or "fig. 1" in low or "fig 1" in low)):
        page_idx=i;page_text=txt;break
if page_idx is None:
    for i,p in enumerate(doc):
        txt=p.get_text("text"); low=" ".join(txt.lower().split())
        if "artemisia annua" in low and "fragmented" in low and ("inflorescence" in low or "inﬂorescence" in low):
            page_idx=i;page_text=txt;break
if page_idx is None:
    for i,p in enumerate(doc):
        txt=p.get_text("text")
        print("M5_057_TEXT_PAGE",i+1,txt[:500].replace("\n"," | "),flush=True)
    raise RuntimeError("Figure 1 page not found after fuzzy validation")
page=doc[page_idx]
pix=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False)
pagepng=OUT/f"m5_057_fig1_page_{page_idx+1}.png";pix.save(str(pagepng))
imgs=[]
for k,img in enumerate(page.get_images(full=True),1):
    xref=img[0];ex=doc.extract_image(xref);data=ex["image"]
    if len(data)<10000:continue
    try:
        im=Image.open(io.BytesIO(data));w,h=im.size;fmt=im.format
    except Exception:continue
    p=OUT/f"m5_057_fig1_xref{xref}_{k}.{ex['ext']}";p.write_bytes(data)
    s1,s256=hh(data)
    imgs.append({"xref":xref,"file":str(p),"bytes":len(data),"width":w,"height":h,"format":fmt,"sha1":s1,"sha256":s256})
# Controlled derivative: Fig. 1b herbal-drug panel only.
# The embedded Fig. 1 composite is 748x413; x=236 cleanly excludes panel a and the black separator.
if not imgs:
    raise RuntimeError("No embedded Fig 1 image extracted")
src_path=pathlib.Path(imgs[0]["file"])
im=Image.open(src_path).convert("RGB")
if im.size != (748,413):
    raise RuntimeError(f"Unexpected Fig 1 composite size {im.size}; do not apply stale crop coordinates")
crop_box=(236,0,748,413)
drug=im.crop(crop_box)
drug_path=OUT/"m5_057_fig1b_herbal_drug_crop.png"
drug.save(drug_path,format="PNG",optimize=False)
drug_bytes=drug_path.read_bytes()
ds1,ds256=hh(drug_bytes)
derivative={"file":str(drug_path),"crop_box":crop_box,"width":drug.width,"height":drug.height,
            "bytes":len(drug_bytes),"sha1":ds1,"sha256":ds256,
            "transformation":"crop only; Fig 1b herbal-drug panel; lossless PNG derivative"}
manifest={"id":57,"article":"Gavaric N et al. Pharmaceutics 2025;17:890","doi":"10.3390/pharmaceutics17070890",
 "license":"CC BY 4.0","resolved_pdf_url":r.url,"pdf_file":str(pp),"pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,
 "figure_page":page_idx+1,"page_text_excerpt":page_text[:5000],"images":imgs,"controlled_derivative":derivative}
(OUT/"extract_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_057_PAGE",page_idx+1,"IMAGES",json.dumps(imgs),flush=True)
print("M5_057_DERIVATIVE="+json.dumps(derivative,ensure_ascii=False),flush=True)
print("M5_057_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
