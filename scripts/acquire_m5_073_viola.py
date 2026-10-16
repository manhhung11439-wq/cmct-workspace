# CMCT T1 M5 #73 exact Viola yedoensis dry medicinal parts from Molecules 2025 Figure 2D
import io,json,hashlib,pathlib,time
import requests,fitz
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_073_viola");OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/3.8 exact Viola yedoensis dry medicinal-parts extraction"
def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True);last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i)));continue
        r.raise_for_status();return r
    last.raise_for_status()
def hh(data):return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()
pdf_url="https://www.mdpi.com/1420-3049/30/9/1922/pdf"
r=get(pdf_url);pdf=r.content
if not pdf.startswith(b"%PDF"):raise RuntimeError("not PDF")
pp=OUT/"m5_073_article_original.pdf";pp.write_bytes(pdf);ps1,ps256=hh(pdf)
doc=fitz.open(stream=pdf,filetype="pdf")
page_idx=None;page_text=""
for i,p in enumerate(doc):
    txt=p.get_text("text"); low=" ".join(txt.lower().split())
    if "figure 2." in low and "dry medicinal parts" in low and "viola yedoensis" in low:
        page_idx=i;page_text=txt;break
if page_idx is None:
    for i,p in enumerate(doc):
        txt=p.get_text("text"); low=" ".join(txt.lower().split())
        if "plant morphology" in low and "dry medicinal parts" in low:
            page_idx=i;page_text=txt;break
if page_idx is None: raise RuntimeError("Figure 2 page not found")
page=doc[page_idx]
pix=page.get_pixmap(matrix=fitz.Matrix(2.4,2.4),alpha=False);pagepng=OUT/f"m5_073_fig2_page_{page_idx+1}.png";pix.save(str(pagepng))
imgs=[]
for k,img in enumerate(page.get_images(full=True),1):
    xref=img[0];ex=doc.extract_image(xref);data=ex["image"]
    if len(data)<10000:continue
    try:
        im=Image.open(io.BytesIO(data));w,h=im.size;fmt=im.format
    except Exception:continue
    p=OUT/f"m5_073_fig2_xref{xref}_{k}.{ex['ext']}";p.write_bytes(data)
    s1,s256=hh(data);imgs.append({"xref":xref,"file":str(p),"bytes":len(data),"width":w,"height":h,"format":fmt,"sha1":s1,"sha256":s256})
manifest={"id":73,"article":"A Comprehensive Review of the Phytochemistry and Therapeutic Efficacy of Viola yedoensis Makino","journal":"Molecules 2025;30(9):1922","doi":"10.3390/molecules30091922","license":"CC BY 4.0","resolved_pdf_url":r.url,"pdf_file":str(pp),"pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,"figure_page":page_idx+1,"page_text_excerpt":page_text[:7500],"images":imgs}
(OUT/"extract_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_073_PAGE",page_idx+1,"IMAGES",json.dumps(imgs),flush=True)
print("M5_073_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
