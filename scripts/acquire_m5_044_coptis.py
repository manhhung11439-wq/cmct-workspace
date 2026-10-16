import requests,pathlib,json,hashlib,time
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_044_coptis"); OUT.mkdir(parents=True,exist_ok=True)
article="https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0153127"
figurl="https://journals.plos.org/plosone/article/figure/image?size=large&id=10.1371/journal.pone.0153127.g001"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.3 exact Coptis dried-rhizome figure"
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(30,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
def hh(data): return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()
page=get(article).text
if "Creative Commons Attribution License" not in page or "Coptis chinensis" not in page or "dried rhizome (Rhizoma Coptidis)" not in page:
  raise RuntimeError("article identity/license/caption assertion failed")
r=get(figurl); data=r.content
ct=(r.headers.get("content-type") or "").lower()
if len(data)<10000: raise RuntimeError("unexpected small figure")
ext=".png" if "png" in ct else ".jpg" if ("jpeg" in ct or "jpg" in ct) else ".bin"
p=OUT/("coptis_fig1_original"+ext); p.write_bytes(data)
s1,s256=hh(data)
im=Image.open(p).convert("RGB")
if im.size != (1996,1651):
  raise RuntimeError(f"unexpected figure size {im.size}; stale crop forbidden")
crop_box=(1235,0,1996,870)
panel=im.crop(crop_box)
cp=OUT/"m5_044_coptis_dried_rhizome_panelB.png"
panel.save(cp,format="PNG",optimize=False)
cb=cp.read_bytes(); cs1,cs256=hh(cb)
manifest={
 "id":44,
 "article_url":article,
 "doi":"10.1371/journal.pone.0153127",
 "authors":"Xiang K-L, Wu S-D, Yu S-X, Liu Y, Jabbour F, Erst AS, et al.",
 "year":2016,
 "figure_id":"g001",
 "caption":"Fig 1. Coptis chinensis. A, plants; B, dried rhizome (Rhizoma Coptidis); C, carpels.",
 "figure_url":r.url,
 "license":"CC BY 4.0",
 "license_url":"https://creativecommons.org/licenses/by/4.0/",
 "original":{"file":str(p),"content_type":ct,"width":im.width,"height":im.height,"bytes":len(data),"sha1":s1,"sha256":s256},
 "controlled_derivative":{"file":str(cp),"crop_box":crop_box,"width":panel.width,"height":panel.height,"bytes":len(cb),"sha1":cs1,"sha256":cs256,
 "transformation":"crop only from original Fig.1; retains panel B dried rhizomes only; excludes living plant panel A and carpels panel C"}
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_044_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
