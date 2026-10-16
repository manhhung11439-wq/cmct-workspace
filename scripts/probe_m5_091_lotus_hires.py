import re,json,pathlib,hashlib,requests,urllib.parse
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_091_lotus_hires"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/10.1"
urls=[
 "https://www.mdpi.com/2304-8158/12/1/198",
 "https://www.mdpi.com/2304-8158/12/1/198/xml",
 "https://mdpi-res.com/d_attachment/foods/foods-12-00198/article_deploy/html/images/foods-12-00198-g001.png",
 "https://mdpi-res.com/d_attachment/foods/foods-12-00198/article_deploy/html/images/foods-12-00198-g001.jpg",
 "https://pub.mdpi-res.com/foods/foods-12-00198/article_deploy/html/images/foods-12-00198-g001.png",
 "https://pub.mdpi-res.com/foods/foods-12-00198/article_deploy/html/images/foods-12-00198-g001.jpg"
]
seen=[]; assets=[]; q=list(urls); done=set()
while q:
    u=q.pop(0)
    if u in done: continue
    done.add(u)
    try:
        r=s.get(u,timeout=120,allow_redirects=True)
        ct=r.headers.get("content-type","")
        rec={"url":u,"final":r.url,"status":r.status_code,"content_type":ct,"bytes":len(r.content)}
        seen.append(rec)
        if r.ok and ("text/html" in ct or "xml" in ct):
            txt=r.text
            (OUT/f"page_{len(seen)}.txt").write_text(txt,encoding="utf-8",errors="ignore")
            for m in re.findall(r'''(?:src|href)=["']([^"']*foods-12-00198-g001[^"']*)["']''',txt,re.I):
                uu=urllib.parse.urljoin(r.url,m.replace("&amp;","&"))
                if uu not in done: q.append(uu)
        if r.ok and ct.startswith("image/"):
            ext=".png" if "png" in ct else ".jpg"
            p=OUT/f"asset_{len(assets)+1}{ext}"; p.write_bytes(r.content)
            try:
                im=Image.open(p); im.load()
                assets.append({**rec,"file":str(p),"width":im.width,"height":im.height,"format":im.format,
                               "sha1":hashlib.sha1(r.content).hexdigest(),"sha256":hashlib.sha256(r.content).hexdigest()})
            except: pass
    except Exception as e: seen.append({"url":u,"error":repr(e)})
man={"requests":seen,"assets":assets}
(OUT/"manifest.json").write_text(json.dumps(man,indent=2),encoding="utf-8")
print(json.dumps(man,indent=2),flush=True)
