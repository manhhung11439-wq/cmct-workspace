import re, json, pathlib, hashlib, requests, urllib.parse, time
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_025_ssp_mdpi_hi_res"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/8.3"
urls=[
 "https://www.mdpi.com/2304-8158/14/4/671",
 "https://www.mdpi.com/2304-8158/14/4/671/xml",
 "https://mdpi-res.com/d_attachment/foods/foods-14-00671/article_deploy/html/images/foods-14-00671-g001.png",
 "https://mdpi-res.com/d_attachment/foods/foods-14-00671/article_deploy/html/images/foods-14-00671-g001.jpg",
 "https://pub.mdpi-res.com/foods/foods-14-00671/article_deploy/html/images/foods-14-00671-g001.png",
 "https://pub.mdpi-res.com/foods/foods-14-00671/article_deploy/html/images/foods-14-00671-g001.jpg"
]
seen=[]; assets=[]
for u in urls:
  try:
    r=s.get(u,timeout=120,allow_redirects=True)
    rec={"url":u,"final":r.url,"status":r.status_code,"content_type":r.headers.get("content-type"),"bytes":len(r.content)}
    seen.append(rec)
    if r.ok and ("text/html" in (r.headers.get("content-type") or "") or "xml" in (r.headers.get("content-type") or "")):
      txt=r.text
      (OUT/f"page_{len(seen)}.txt").write_text(txt,encoding="utf-8",errors="ignore")
      for m in re.findall(r'''(?:src|href)=["']([^"']*foods-14-00671-g001[^"']*)["']''',txt,re.I):
        uu=urllib.parse.urljoin(r.url,m.replace("&amp;","&"))
        if uu not in urls: urls.append(uu)
    if r.ok and (r.headers.get("content-type") or "").startswith("image/"):
      ext=".png" if "png" in r.headers.get("content-type","") else ".jpg"
      p=OUT/f"asset_{len(assets)+1}{ext}"; p.write_bytes(r.content)
      try:
        im=Image.open(p); im.load()
        sha1=hashlib.sha1(r.content).hexdigest(); sha256=hashlib.sha256(r.content).hexdigest()
        assets.append({**rec,"file":str(p),"width":im.width,"height":im.height,"format":im.format,"sha1":sha1,"sha256":sha256})
      except Exception as e: pass
  except Exception as e: seen.append({"url":u,"error":repr(e)})
man={"requests":seen,"assets":assets}
(OUT/"manifest.json").write_text(json.dumps(man,indent=2),encoding="utf-8")
print(json.dumps(man,indent=2),flush=True)
