import requests,pathlib,json,hashlib,time
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_047_forsythia"); OUT.mkdir(parents=True,exist_ok=True)
url="https://www.frontiersin.org/files/Articles/758326/xml-images/fgene-12-758326-g001.webp"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.5 exact Forsythiae Fructus figure"
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
p=OUT/"forsythia_fig1_original.webp"; p.write_bytes(data)
s1,s256=hh(data)
im=Image.open(p).convert("RGB")
if im.size != (1500,418):
  raise RuntimeError(f"unexpected figure size {im.size}; stale crop forbidden")
crop_box=(1025,38,1498,415)
drug=im.crop(crop_box)
cp=OUT/"m5_047_forsythiae_fructus_panelC.png"
drug.save(cp,format="PNG",optimize=False)
cb=cp.read_bytes(); cs1,cs256=hh(cb)
manifest={"id":47,"doi":"10.3389/fgene.2021.758326",
 "article":"Wu B, Li Y, Zhao W, Meng Z, Ji W, Wang C. Frontiers in Genetics 2021;12:758326",
 "caption":"Figure 1. (A) Forsythia suspensa (Thunb.) Vahl; (B) Forsythia fruit growing on the tree; (C) Forsythiae Fructus as a medicinal material.",
 "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
 "figure_url":r.url,
 "original":{"file":str(p),"width":im.width,"height":im.height,"bytes":len(data),"sha1":s1,"sha256":s256},
 "controlled_derivative":{"file":str(cp),"crop_box":crop_box,"width":drug.width,"height":drug.height,
 "bytes":len(cb),"sha1":cs1,"sha256":cs256,
 "transformation":"crop only from original Figure 1; retains medicinal-material panel C only; excludes living tree/fruit panels A and B"}}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_047_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
