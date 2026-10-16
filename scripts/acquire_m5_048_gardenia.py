import requests,pathlib,json,hashlib,time
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_048_gardenia"); OUT.mkdir(parents=True,exist_ok=True)
url="https://www.frontiersin.org/files/Articles/1712973/xml-images/fsufs-09-1712973-g001.webp"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.7 exact Gardenia mature processed-fruit figure"
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(30,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
def hh(data): return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()
r=get(url); data=r.content
if len(data)<10000: raise RuntimeError("unexpected small image")
p=OUT/"gardenia_fig1_original.webp"; p.write_bytes(data)
s1,s256=hh(data)
im=Image.open(p).convert("RGB")
if im.size != (1535,590):
  raise RuntimeError(f"unexpected figure size {im.size}; stale crop forbidden")
# Figure 1: top row = fresh fruits stages 1-7; bottom row = processed medicinal herbs.
# Stage 6 is fully mature red fruit; keep only bottom-row stage-6 processed material.
crop_box=(1023,276,1211,533)
drug=im.crop(crop_box)
cp=OUT/"m5_048_gardenia_stage6_processed_dried_fruit.png"
drug.save(cp,format="PNG",optimize=False)
cb=cp.read_bytes(); cs1,cs256=hh(cb)
manifest={
 "id":48,
 "doi":"10.3389/fsufs.2025.1712973",
 "authors":"Chai C, Jin B, Cui Y, Cui X, Shan C, Yu S, Wen H",
 "article":"Frontiers in Sustainable Food Systems; published 30 Jan 2026",
 "identity":"Gardenia jasminoides J.Ellis",
 "article_material":"dried mature fruit of Gardenia jasminoides J.Ellis",
 "processing":"remove stalks/impurities; steam 10-15 min; dry at 60 C",
 "maturity_control":"stages 5-6 are mature; stage 6 is fully mature red fruit; selected derivative uses processed stage 6 only",
 "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
 "figure_url":r.url,
 "original":{"file":str(p),"width":im.width,"height":im.height,"bytes":len(data),"sha1":s1,"sha256":s256},
 "controlled_derivative":{"file":str(cp),"crop_box":crop_box,"width":drug.width,"height":drug.height,
 "bytes":len(cb),"sha1":cs1,"sha256":cs256,
 "transformation":"crop only from original Figure 1; retains bottom-row processed medicinal-herb Stage 6 (fully mature red fruit) only; excludes top-row fresh fruits and all other maturity stages"}
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_048_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
