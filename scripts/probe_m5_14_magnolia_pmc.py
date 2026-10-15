import re,hashlib,json,time,html as htmlmod
from pathlib import Path
import requests
from urllib.parse import urljoin
OUT=Path("evidence/m5_14_magnolia_pmc"); OUT.mkdir(parents=True,exist_ok=True)
url="https://pmc.ncbi.nlm.nih.gov/articles/PMC12157075/"
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/2.1 scientific-figure provenance"
r=s.get(url,timeout=90);r.raise_for_status()
txt=r.text
(OUT/"article.html").write_text(txt,encoding="utf-8")
# capture figure blocks and img src/href/caption text
blocks=re.findall(r'(<figure[^>]*>.*?</figure>)',txt,flags=re.S|re.I)
if not blocks:
    blocks=re.findall(r'(<div[^>]+class="[^"]*(?:fig|figure)[^"]*"[^>]*>.*?</div>)',txt,flags=re.S|re.I)
recs=[]
for idx,b in enumerate(blocks,1):
    cap=re.sub(r'<[^>]+>',' ',b)
    cap=" ".join(htmlmod.unescape(cap).split())
    srcs=re.findall(r'(?:src|href)="([^"]+\.(?:jpg|jpeg|png|tif|tiff|webp)(?:\?[^"]*)?)"',b,flags=re.I)
    srcs=list(dict.fromkeys(srcs))
    if not srcs:continue
    for j,src in enumerate(srcs,1):
        u=urljoin(url,src)
        try:
            rr=s.get(u,timeout=90);rr.raise_for_status()
        except Exception as e:
            print("FAIL",idx,u,e,flush=True);continue
        ext=".jpg"
        ct=(rr.headers.get("content-type") or "").lower()
        if "png" in ct:ext=".png"
        elif "webp" in ct:ext=".webp"
        elif "tif" in ct:ext=".tif"
        fn=f"figure_{idx}_{j}{ext}"
        (OUT/fn).write_bytes(rr.content)
        rec={"figure":idx,"file":fn,"url":u,"caption":cap,"bytes":len(rr.content),
             "sha1":hashlib.sha1(rr.content).hexdigest(),"sha256":hashlib.sha256(rr.content).hexdigest(),"content_type":ct}
        recs.append(rec)
        print("FIG",idx,fn,"bytes",len(rr.content),"caption",cap[:700],flush=True)
(OUT/"figures.json").write_text(json.dumps(recs,ensure_ascii=False,indent=2),encoding="utf-8")
print("TOTAL",len(recs),flush=True)
