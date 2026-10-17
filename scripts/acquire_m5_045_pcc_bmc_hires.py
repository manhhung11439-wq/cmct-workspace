import json,hashlib,pathlib,time,requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_045_pcc_bmc_hires"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/28.1 PCC Figure1 high-res probe"
base="https://media.springernature.com/{size}/springer-static/image/art%3A10.1186%2Fs12951-021-00847-y/MediaObjects/12951_2021_847_Fig1_HTML.jpg"
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
assets=[]
for size in ["full","lw1200","lw1000","lw685"]:
    u=base.format(size=size)
    try:
        r=s.get(u,timeout=60,allow_redirects=True); r.raise_for_status()
        b=r.content; p=OUT/f"figure1_{size}.jpg"; p.write_bytes(b)
        im=Image.open(p); im.load(); s1,s256=hh(b)
        assets.append({"size":size,"url":r.url,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
    except Exception as e:
        print("FAIL",size,repr(e),flush=True)
if not assets: raise RuntimeError("No Springer/BMC Figure1 asset")
assets.sort(key=lambda x:x["width"]*x["height"],reverse=True)
man={"id":45,"doi":"10.1186/s12951-021-00847-y","assets":assets,"best":assets[0],
     "license_basis":"Article PMC8048166 CC BY 4.0; Figure 1 has no separate contrary credit line."}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(man,ensure_ascii=False,indent=2),flush=True)
