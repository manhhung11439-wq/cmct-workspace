# CMCT T1 M5 #54/#56 public-domain specimen atlas discovery
import json,hashlib,pathlib,time,re,html
import requests,fitz

OUT=pathlib.Path("evidence/m5_t1_054_056_specimen_atlas"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/3.5 exact medicinal specimen atlas discovery"
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
params={"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2}
meta=get(api,params=params).json(); page=(meta.get("query",{}).get("pages") or [{}])[0]
if page.get("missing"): raise RuntimeError("Commons atlas missing")
ii=(page.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
md={k:clean(em.get(k) or "") for k in ["LicenseShortName","LicenseUrl","UsageTerms","Artist","Credit","ImageDescription","Categories"]}
url=ii["url"]; r=get(url); pdf=r.content
if not pdf.startswith(b"%PDF"): raise RuntimeError("not PDF")
p=OUT/"specimen_atlas_original.pdf"; p.write_bytes(pdf)
sha1=hashlib.sha1(pdf).hexdigest(); sha256=hashlib.sha256(pdf).hexdigest()
doc=fitz.open(stream=pdf,filetype="pdf")
targets={"54":["射干","belamcanda","iris domestica"],"56":["地骨皮","lycii cortex","cortex radicis lycii"]}
hits={k:[] for k in targets}
for i,pg in enumerate(doc):
    txt=pg.get_text("text") or ""
    norm=" ".join(txt.split())
    low=norm.lower()
    for rid,terms in targets.items():
        if any((t.lower() in low if t.isascii() else t in norm) for t in terms):
            hits[rid].append({"page":i+1,"text":norm[:3000]})
for rid,hs in hits.items():
    for h in hs[:12]:
        i=h["page"]-1
        for j in range(max(0,i-1),min(len(doc),i+2)):
            pix=doc[j].get_pixmap(matrix=fitz.Matrix(1.7,1.7),alpha=False)
            pix.save(str(OUT/f"rid{rid}_candidate_page_{j+1}.png"))
manifest={"commons_title":title,"resolved_url":url,"commons_sha1":ii.get("sha1"),"bytes":len(pdf),
          "sha1":sha1,"sha256":sha256,"page_count":len(doc),"metadata":md,"hits":hits}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("ATLAS_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
