import json,hashlib,pathlib,time,re,requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_090_sauropus_springer"); OUT.mkdir(parents=True,exist_ok=True)
ARTICLE="https://link.springer.com/article/10.1186/s42779-022-00125-8"
base="https://media.springernature.com/{size}/springer-static/image/art%3A10.1186%2Fs42779-022-00125-8/MediaObjects/42779_2022_125_Fig4_HTML.jpg"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/27.1 Sauropus Figure4 direct Springer asset"
def get(u):
    last=None
    for i in range(6):
        r=s.get(u,timeout=60,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(20,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
ar=get(ARTICLE); (OUT/"article.html").write_bytes(ar.content)
html=ar.text
caption="Preparation of stir-fried S. androgynus in Kerala. A. Collection of the compound leaves from the plant. B. Separation of the leaflets from the rachis."
license_ok=("Creative Commons Attribution 4.0 International License" in html or "creativecommons.org/licenses/by/4.0" in html)
assets=[]
for size in ["full","lw1200","lw1000","lw685"]:
    u=base.format(size=size)
    try:
        r=get(u); b=r.content
        p=OUT/f"figure4_{size}.jpg"; p.write_bytes(b)
        im=Image.open(p); im.load()
        s1,s256=hh(b)
        assets.append({"size_variant":size,"url":r.url,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
    except Exception as e:
        print("ASSET_FAIL",size,repr(e),flush=True)
if not assets: raise RuntimeError("No Springer Figure 4 asset acquired")
assets.sort(key=lambda x:x["width"]*x["height"],reverse=True)
best=assets[0]
man={"id":90,"target":"Rau Ngót / Sauropus androgynus (L.) Merr.","article_url":ARTICLE,
     "article_title":"Sauropus androgynus (L.) Merr.: a multipurpose plant with multiple uses in traditional ethnic culinary and ethnomedicinal preparations",
     "doi":"10.1186/s42779-022-00125-8","article_license":"CC BY 4.0" if license_ok else "UNVERIFIED",
     "figure_caption":caption,"assets":assets,"best_original":best,
     "controller_status":"BEST OFFICIAL SPRINGER ASSET ACQUIRED; PANEL B CROP REQUIRES VISUAL LOCK"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
