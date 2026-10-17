import json,hashlib,pathlib,time,requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_082_houttuynia_dry_direct"); OUT.mkdir(parents=True,exist_ok=True)
URL="https://www.frontiersin.org/files/Articles/714694/xml-images/fphar-12-714694-g001.webp"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/29.1 Houttuynia Frontiers Figure1 direct"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
r=get(URL); b=r.content
p=OUT/"figure1_original.webp"; p.write_bytes(b)
im=Image.open(p); im.load(); s1,s256=hh(b)
man={
"id":82,
"target":"Diếp Cá / Houttuynia cordata Thunb.",
"article":"Wu Z. et al. Houttuynia cordata Thunb: An Ethnopharmacological Review. Front Pharmacol. 2021;12:714694.",
"doi":"10.3389/fphar.2021.714694",
"license":"CC BY",
"figure_caption":"Climatic and ecological adaptability distribution of H. cordata in China (A) flowers of H. cordata (B) roots of H. cordata as food (C) above-ground part of dry stems and leaves of H. cordata.",
"original_url":r.url,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256,
"controller_status":"OFFICIAL FRONTIERS FIGURE 1 ACQUIRED; PANEL C CROP REQUIRES VISUAL LOCK"
}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
