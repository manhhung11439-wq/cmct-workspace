import pathlib,hashlib,json,requests,time
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_094_pulsatilla_hires"); OUT.mkdir(parents=True,exist_ok=True)
base="springer-static/image/art%3A10.1038%2Fsrep40000/MediaObjects/41598_2017_Article_BFsrep40000_Fig3_HTML.jpg"
urls=[
 f"https://media.springernature.com/full/{base}",
 f"https://media.springernature.com/lw1200/{base}",
 f"https://media.springernature.com/lw685/{base}",
]
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/9.1"
assets=[]
for i,u in enumerate(urls,1):
  try:
    r=s.get(u,timeout=180,allow_redirects=True)
    rec={"url":u,"final_url":r.url,"status":r.status_code,"content_type":r.headers.get("content-type"),"bytes":len(r.content)}
    if r.ok and (r.headers.get("content-type") or "").startswith("image/"):
      p=OUT/f"asset_{i}.jpg"; p.write_bytes(r.content)
      im=Image.open(p); im.load()
      rec.update(file=str(p),width=im.width,height=im.height,format=im.format,
        sha1=hashlib.sha1(r.content).hexdigest(),sha256=hashlib.sha256(r.content).hexdigest())
      assets.append(rec)
    print(json.dumps(rec),flush=True)
  except Exception as e:
    print(json.dumps({"url":u,"error":repr(e)}),flush=True)
man={"assets":assets,"best":max(assets,key=lambda x:x["width"]*x["height"]) if assets else None}
(OUT/"manifest.json").write_text(json.dumps(man,indent=2),encoding="utf-8")
if not assets: raise RuntimeError("No publisher Figure 3 asset acquired")
print("BEST="+json.dumps(man["best"]),flush=True)
