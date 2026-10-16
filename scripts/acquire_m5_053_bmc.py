# CMCT T1 M5 #53 exact prepared Isatidis Radix from CC-BY Chinese Medicine Fig 3d
import io,re,json,hashlib,pathlib,time
import requests,fitz
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_053_banlangen_bmc");OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/2.9 exact BMC Isatidis Radix figure extraction"
def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True);last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i)));continue
        r.raise_for_status();return r
    last.raise_for_status()
def hh(data):return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()

pdf_url="https://cmjournal.biomedcentral.com/counter/pdf/10.1186/s13020-023-00777-x"
r=get(pdf_url);pdf=r.content
if not pdf.startswith(b"%PDF"):raise RuntimeError("Not PDF: "+r.url+" "+str(r.headers.get("content-type")))
pp=OUT/"m5_053_BMC_article_original.pdf";pp.write_bytes(pdf);ps1,ps256=hh(pdf)
doc=fitz.open(stream=pdf,filetype="pdf")
page_idx=None;page_text=""
for i,p in enumerate(doc):
    txt=p.get_text("text")
    if "Fig. 3" in txt and "Isatidis Radix (BBLG)" in txt:
        page_idx=i;page_text=txt;break
if page_idx is None:raise RuntimeError("Fig 3 page not found")
page=doc[page_idx]
pix=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False)
pagepng=OUT/f"m5_053_fig3_page_{page_idx+1}.png";pix.save(str(pagepng))
imgs=[]
for k,img in enumerate(page.get_images(full=True),1):
    xref=img[0];ex=doc.extract_image(xref);data=ex["image"]
    if len(data)<15000:continue
    try:
        im=Image.open(io.BytesIO(data));w,h=im.size;fmt=im.format
    except Exception:continue
    path=OUT/f"m5_053_fig3_xref{xref}_{k}.{ex['ext']}";path.write_bytes(data)
    s1,s256=hh(data)
    imgs.append({"xref":xref,"file":str(path),"bytes":len(data),"width":w,"height":h,"format":fmt,"sha1":s1,"sha256":s256})
print("BMC53_PAGE",page_idx+1,"IMAGES",json.dumps(imgs),flush=True)
manifest={"id":53,"article":"Li Y et al. Chinese Medicine 2023;18:65","doi":"10.1186/s13020-023-00777-x",
 "license":"CC BY 4.0","resolved_pdf_url":r.url,"pdf_file":str(pp),"pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,
 "figure_page":page_idx+1,"page_text_excerpt":page_text[:5000],"images":imgs}
(OUT/"extract_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("BMC53_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
