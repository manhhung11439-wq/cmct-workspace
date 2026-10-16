# CMCT T1 M5 #70 exact Sophora flavescens dried-root scientific figure acquisition
import io,json,hashlib,pathlib,time
import requests,fitz
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_070_sophora");OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/3.6 exact Sophora flavescens dried-root figure extraction"
def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True);last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i)));continue
        r.raise_for_status();return r
    last.raise_for_status()
def hh(data):return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()
pdf_url="https://www.mdpi.com/1424-8247/15/11/1384/pdf"
r=get(pdf_url);pdf=r.content
if not pdf.startswith(b"%PDF"):raise RuntimeError("not PDF")
pp=OUT/"m5_070_article_original.pdf";pp.write_bytes(pdf);ps1,ps256=hh(pdf)
doc=fitz.open(stream=pdf,filetype="pdf")
page_idx=None;page_text=""
for i,p in enumerate(doc):
    txt=p.get_text("text")
    low=" ".join(txt.lower().split())
    if "figure 1." in low and "dried root" in low and "sophora flavescens" in low:
        page_idx=i;page_text=txt;break
if page_idx is None:
    for i,p in enumerate(doc):
        txt=p.get_text("text"); low=" ".join(txt.lower().split())
        if "fresh plant" in low and "dried root" in low and "root cross-section" in low:
            page_idx=i;page_text=txt;break
if page_idx is None: raise RuntimeError("Figure 1 page not found")
page=doc[page_idx]
pix=page.get_pixmap(matrix=fitz.Matrix(2.4,2.4),alpha=False)
pagepng=OUT/f"m5_070_fig1_page_{page_idx+1}.png";pix.save(str(pagepng))
imgs=[]
for k,img in enumerate(page.get_images(full=True),1):
    xref=img[0];ex=doc.extract_image(xref);data=ex["image"]
    if len(data)<10000:continue
    try:
        im=Image.open(io.BytesIO(data));w,h=im.size;fmt=im.format
    except Exception:continue
    p=OUT/f"m5_070_fig1_xref{xref}_{k}.{ex['ext']}";p.write_bytes(data)
    s1,s256=hh(data);imgs.append({"xref":xref,"file":str(p),"bytes":len(data),"width":w,"height":h,"format":fmt,"sha1":s1,"sha256":s256})
# Controlled derivative: Figure 1D (dried root) only.
src=[x for x in imgs if x["sha256"]=="f04f1c1d0486d06ed7eb0372539bdbd429e782f3593ab9d20f77cc80e5bc6c1e"]
if len(src)!=1: raise RuntimeError(f"Expected exact Figure 1 composite hash once, got {len(src)}")
src_path=pathlib.Path(src[0]["file"])
im=Image.open(src_path).convert("RGB")
if im.size!=(3183,663): raise RuntimeError(f"Unexpected Figure 1 size {im.size}; stale crop prohibited")
crop_box=(1629,0,2390,663)
drug=im.crop(crop_box)
drug_path=OUT/"m5_070_fig1D_dried_root_crop.png"
drug.save(drug_path,format="PNG",optimize=False)
db=drug_path.read_bytes();ds1,ds256=hh(db)
derivative={"file":str(drug_path),"source_image_sha256":src[0]["sha256"],"crop_box":crop_box,
"width":drug.width,"height":drug.height,"bytes":len(db),"sha1":ds1,"sha256":ds256,
"transformation":"crop only from original embedded Figure 1 composite; retains panel D dried root; excludes panels A-C and E"}

manifest={"id":70,"article":"Determination of Antioxidant, Cytotoxicity, and Acetylcholinesterase Inhibitory Activities of Alkaloids Isolated from Sophora flavescens Ait. Grown in Dak Nong, Vietnam","journal":"Pharmaceuticals 2022;15(11):1384","doi":"10.3390/ph15111384","license":"CC BY 4.0","resolved_pdf_url":r.url,"pdf_file":str(pp),"pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,"figure_page":page_idx+1,"page_text_excerpt":page_text[:7000],"images":imgs,"controlled_derivative":derivative}
(OUT/"extract_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_070_PAGE",page_idx+1,"IMAGES",json.dumps(imgs),flush=True)
print("M5_070_DERIVATIVE="+json.dumps(derivative,ensure_ascii=False),flush=True)
print("M5_070_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
