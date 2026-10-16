import json,hashlib,pathlib,time,re,html
import requests,fitz
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_atlas_pass_006_008_009_010"); OUT.mkdir(parents=True,exist_ok=True)
TITLE="File:NLC416-08jh015896-38387 中國藥物標本圖影.pdf"
EXPECTED_PDF_SHA1="1aef378d7c63ab41a2ddd116b492da98e63cae75"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/5.3 PD atlas controlled crops T1 M5 6 8 9 10"
api="https://commons.wikimedia.org/w/api.php"
def get(url,params=None):
    last=None
    for i in range(8):
        r=s.get(url,params=params,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
def clean(v):
    if isinstance(v,dict): v=v.get("value") or ""
    v=html.unescape(str(v or "")); v=re.sub(r"<[^>]+>"," ",v)
    return " ".join(v.split())

meta=get(api,{"action":"query","titles":TITLE,"prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2}).json()
p=meta["query"]["pages"][0]; ii=p["imageinfo"][0]; em=ii.get("extmetadata") or {}
url=ii["url"]
pdf=get(url).content
ps1,ps256=hh(pdf)
if ps1!=EXPECTED_PDF_SHA1: raise SystemExit(f"atlas SHA1 mismatch {ps1}")
(OUT/"atlas_original.pdf").write_bytes(pdf)
source_meta={
 "commons_title":TITLE,"resolved_url":url,"commons_sha1":ii.get("sha1"),
 "pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,
 "artist":clean(em.get("Artist")),"credit":clean(em.get("Credit")),
 "license":clean(em.get("LicenseShortName")),"license_url":clean(em.get("LicenseUrl")),
 "description":clean(em.get("ImageDescription")),"categories":clean(em.get("Categories")),
}
doc=fitz.open(stream=pdf,filetype="pdf")
# PDF page numbers are 1-based below. Crops were controller-verified on Matrix(2.0,2.0) renders.
rows={
 6:{"drug":"防風","name":"Phòng Phong","pdf_page":61,"image_page":46,"crop":[245,580,650,925],
    "target":"Saposhnikovia divaricata; dried root"},
 8:{"drug":"桂枝","name":"Quế Chi","pdf_page":201,"image_page":186,"crop":[450,600,880,920],
    "target":"Cinnamomum cassia; dried young branch/twig"},
 9:{"drug":"荊芥","name":"Kinh Giới","pdf_page":75,"image_page":60,"crop":[420,650,1020,1120],
    "target":"Schizonepeta tenuifolia (accepted Nepeta tenuifolia); dried aerial parts"},
10:{"drug":"薄荷","name":"Bạc Hà","pdf_page":79,"image_page":64,"crop":[250,260,600,620],
    "target":"Mentha canadensis (incl. medicinal-source Mentha haplocalyx); dried aerial parts"},
}
manifest={"source":source_meta,"render_matrix":[2.0,2.0],"rows":{}}
for rid,rec in rows.items():
    page=doc[rec["pdf_page"]-1]
    pix=page.get_pixmap(matrix=fitz.Matrix(2.0,2.0),alpha=False)
    full=OUT/f"m5_{rid:03d}_atlas_page_{rec['pdf_page']:03d}.png"; pix.save(str(full))
    fb=full.read_bytes(); fs1,fs256=hh(fb)
    im=Image.open(full).convert("RGB")
    crop=im.crop(tuple(rec["crop"]))
    cf=OUT/f"m5_{rid:03d}_{rec['name'].replace(' ','_')}_controlled_crop.png"
    crop.save(cf,format="PNG",optimize=False)
    cb=cf.read_bytes(); cs1,cs256=hh(cb)
    manifest["rows"][str(rid)]={**rec,
      "page_render":{"file":str(full),"width":im.width,"height":im.height,"bytes":len(fb),"sha1":fs1,"sha256":fs256},
      "controlled_derivative":{"file":str(cf),"width":crop.width,"height":crop.height,"bytes":len(cb),"sha1":cs1,"sha256":cs256},
      "transformation":"render original PD atlas page at Matrix(2.0,2.0), then crop only; no medicinal-material content alteration"}
    print("ATLAS_PASS_CANDIDATE",rid,json.dumps(manifest["rows"][str(rid)],ensure_ascii=False),flush=True)
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("ATLAS_SOURCE="+json.dumps(source_meta,ensure_ascii=False),flush=True)
