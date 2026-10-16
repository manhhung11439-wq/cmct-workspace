# CMCT reproducible CC-BY derivative crops for M5 #43/#53 from exact original PDFs
import io,json,hashlib,pathlib,time
import requests,fitz
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_fullgate_scifig_43_53");OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/2.8 reproducible scientific figure crop"
def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True);last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i)));continue
        r.raise_for_status();return r
    last.raise_for_status()
def h(data):
    return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()
def save_png(im,path):
    im.save(path,format="PNG",optimize=False)
    data=path.read_bytes();return len(data),*h(data)

jobs=[
 {"id":53,"pdf":"https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2021.685575/pdf",
  "needle":["A photograph of the dried root","Isatis indigotica"],"crop":(0,0,640,308),
  "license":"CC BY","license_url":"https://creativecommons.org/licenses/by/4.0/",
  "authors":"Li-Xing Nie, Jing Dong, Lie-Yan Huang, Xiu-Yu Qian, Chao-Jie Lian, Shuai Kang, Zhong Dai, Shuang-Cheng Ma",
  "citation":"Nie L-X et al. (2021) Frontiers in Pharmacology 12:685575. Fig. 1A.",
  "caption":"Dried root of Isatis tinctoria (syn. Isatis indigotica), cropped from Fig. 1A; change: cropped to medicinal-material panel only."},
 {"id":43,"pdf":"https://link.springer.com/content/pdf/10.1007/s11434-016-1136-5.pdf",
  "needle":["The medicinal plant Scutellaria baicalensis","dried root"],"crop":(670,0,969,330),
  "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
  "authors":"Qing Zhao, Xiao-Ya Chen, Cathie Martin",
  "citation":"Zhao Q, Chen X-Y, Martin C. (2016) Science Bulletin 61:1391–1398. Fig. 1b.",
  "caption":"Dried root of Scutellaria baicalensis used in traditional Chinese medicine, cropped from Fig. 1b; change: cropped to medicinal-material panel only."}
]
out=[]
for j in jobs:
    r=get(j["pdf"]);pdf=r.content
    if not pdf.startswith(b"%PDF"):raise RuntimeError(f"#{j['id']} PDF fetch failed")
    pp=OUT/f"m5_{j['id']:03d}_article_original.pdf";pp.write_bytes(pdf);ps1,ps256=h(pdf)
    doc=fitz.open(stream=pdf,filetype="pdf")
    pi=None
    for i,p in enumerate(doc):
        txt=p.get_text("text")
        if all(x.lower() in txt.lower() for x in j["needle"]):pi=i;break
    if pi is None:raise RuntimeError(f"#{j['id']} figure page not found")
    imgs=[]
    for img in doc[pi].get_images(full=True):
        ex=doc.extract_image(img[0]);data=ex["image"]
        if len(data)<10000:continue
        try:
            im=Image.open(io.BytesIO(data));w,h0=im.size
        except:continue
        imgs.append((w*h0,len(data),img[0],data,ex["ext"],w,h0))
    if not imgs:raise RuntimeError(f"#{j['id']} no image stream")
    _,_,xref,comp,ext,w,h0=max(imgs,key=lambda z:(z[0],z[1]))
    cp=OUT/f"m5_{j['id']:03d}_figure_composite_original.{ext}";cp.write_bytes(comp)
    cs1,cs256=h(comp)
    im=Image.open(io.BytesIO(comp)).convert("RGB")
    if j["crop"][2]>im.width or j["crop"][3]>im.height:
        raise RuntimeError(f"#{j['id']} crop outside composite {im.size}")
    crop=im.crop(j["crop"])
    dp=OUT/f"m5_{j['id']:03d}_M5_derivative_crop.png"
    dbytes,ds1,ds256=save_png(crop,dp)
    rec={**j,"resolved_pdf_url":r.url,"pdf_file":str(pp),"pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,
         "figure_page":pi+1,"composite_file":str(cp),"composite_bytes":len(comp),"composite_width":w,"composite_height":h0,
         "composite_sha1":cs1,"composite_sha256":cs256,"composite_xref":xref,
         "derivative_file":str(dp),"derivative_width":crop.width,"derivative_height":crop.height,
         "derivative_bytes":dbytes,"derivative_sha1":ds1,"derivative_sha256":ds256,
         "transformation":"crop only; no content addition/removal inside selected panel; PNG lossless derivative"}
    out.append(rec)
    print("FULLGATE_SCIFIG",j["id"],json.dumps(rec,ensure_ascii=False),flush=True)
(OUT/"manifest.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
