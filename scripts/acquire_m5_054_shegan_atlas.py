# CMCT T1 M5 #54 exact Belamcandae Rhizoma from public-domain specimen atlas page 126
import json,hashlib,pathlib,time,re,html
import requests,fitz
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_054_shegan_atlas"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/3.6 exact Shegan crude-drug atlas extraction"
api="https://commons.wikimedia.org/w/api.php"
title="File:NLC416-08jh015896-38387 中國藥物標本圖影.pdf"

def get(url,params=None):
    last=None
    for i in range(8):
        r=s.get(url,params=params,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get("value") or ""
    v=html.unescape(str(v or "")); v=re.sub(r"<[^>]+>"," ",v)
    return " ".join(v.split())
def hh(data): return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()

params={"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2}
meta=get(api,params=params).json(); pg=(meta.get("query",{}).get("pages") or [{}])[0]
ii=(pg.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
md={k:clean(em.get(k) or "") for k in ["LicenseShortName","LicenseUrl","UsageTerms","Artist","Credit","ImageDescription","Categories"]}
if "Public domain" not in (md.get("LicenseShortName","")+" "+md.get("UsageTerms","")):
    raise RuntimeError(f"Atlas is not public-domain per file metadata: {md}")
r=get(ii["url"]); pdf=r.content
if not pdf.startswith(b"%PDF"): raise RuntimeError("not PDF")
pp=OUT/"specimen_atlas_original.pdf"; pp.write_bytes(pdf)
ps1,ps256=hh(pdf)
if ii.get("sha1") and ps1.lower()!=ii.get("sha1").lower():
    raise RuntimeError("Commons SHA1 mismatch")
doc=fitz.open(stream=pdf,filetype="pdf")
page_no=126
page=doc[page_no-1]
pix=page.get_pixmap(matrix=fitz.Matrix(2.2,2.2),alpha=False)
page_path=OUT/"m5_054_atlas_page_126.png"; pix.save(str(page_path))
page_im=Image.open(page_path).convert("RGB")
if page_im.width not in (1308,1309,1310) or page_im.height not in (1852,1853,1854):
    raise RuntimeError(f"Unexpected rendered page size {page_im.size}; stale crop forbidden")
crop_box=(600,520,1080,1100)
drug=page_im.crop(crop_box)
drug_path=OUT/"m5_054_shegan_processed_rhizome_crop.png"
drug.save(drug_path,format="PNG",optimize=False)
db=drug_path.read_bytes(); ds1,ds256=hh(db)
manifest={"id":54,"commons_title":title,"license":md.get("LicenseShortName"),"usage_terms":md.get("UsageTerms"),
"credit":md.get("Credit"),"artist":md.get("Artist"),"resolved_pdf_url":r.url,"pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,
"commons_sha1":ii.get("sha1"),"page":page_no,"page_render_size":page_im.size,
"controlled_derivative":{"file":str(drug_path),"crop_box":crop_box,"width":drug.width,"height":drug.height,
"bytes":len(db),"sha1":ds1,"sha256":ds256,
"transformation":"render original public-domain scan at Matrix(2.2,2.2) + crop only; retains vertical 射干 label and photographed crude-drug rhizome pieces; excludes living-plant panel"}}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_054_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
