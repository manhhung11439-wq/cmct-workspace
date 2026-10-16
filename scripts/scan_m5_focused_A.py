# CMCT T1 focused exact-species processed scan A — 2026-10-16
import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_focused_A"); OUT.mkdir(parents=True,exist_ok=True)
targets={
15:{"cats":["Morus alba"],"terms":["dried leaf","leaf","folium","桑叶","桑葉","herbal medicine","药材","藥材"]},
18:{"cats":["Actaea cimicifuga","Cimicifuga foetida"],"terms":["rhizome","dried","cimicifugae","升麻","herbal medicine","药材","藥材"]},
23:{"cats":["Vitex trifolia"],"terms":["fruit","dried","viticis","蔓荆子","蔓荊子","herbal medicine","药材","藥材"]},
24:{"cats":["Spirodela polyrhiza"],"terms":["dried","whole plant","herb","浮萍","herbal medicine","药材","藥材"]},
33:{"cats":["Paeonia suffruticosa"],"terms":["root bark","cortex","dried","moutan","牡丹皮","herbal medicine","药材","藥材"]},
40:{"cats":["Senna tora","Cassia tora"],"terms":["seed","semen","dried","决明子","決明子","herbal medicine","药材","藥材"]},
}
api="https://commons.wikimedia.org/w/api.php";s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/2.2 focused exact category"
def get(p):
  last=None
  for i in range(6):
    r=s.get(api,params=p,timeout=60);last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(int(r.headers.get("Retry-After") or min(30,2*(2**i))));continue
    r.raise_for_status();return r.json()
  last.raise_for_status()
def clean(v):
  if isinstance(v,dict):v=v.get("value") or ""
  return " ".join(re.sub(r"<[^>]+>"," ",html.unescape(str(v or ""))).split())
out={}
for rid,t in targets.items():
  titles=set()
  for cat in t["cats"]:
    cont=None
    while True:
      p={"action":"query","list":"categorymembers","cmtitle":"Category:"+cat,"cmtype":"file","cmlimit":"500","format":"json","formatversion":2}
      if cont:p["cmcontinue"]=cont
      d=get(p)
      for m in d.get("query",{}).get("categorymembers",[]):titles.add(m["title"])
      cont=(d.get("continue") or {}).get("cmcontinue")
      if not cont:break
  recs=[]; tl=sorted(titles)
  for i in range(0,len(tl),50):
    d=get({"action":"query","titles":"|".join(tl[i:i+50]),"prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2})
    for p in d.get("query",{}).get("pages",[]):
      ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}; e=lambda k:clean(em.get(k) or "")
      rec={"title":p.get("title"),"url":ii.get("url"),"sha1":ii.get("sha1"),"size":ii.get("size"),"width":ii.get("width"),"height":ii.get("height"),
           "license":e("LicenseShortName"),"license_url":e("LicenseUrl"),"author":e("Artist"),"credit":e("Credit"),"description":e("ImageDescription"),"categories":e("Categories")}
      blob=" ".join(str(rec.get(k) or "") for k in ("title","description","categories")).lower()
      score=sum(6 for z in t["terms"] if z.lower() in blob)
      if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu"]): score-=20
      if any(z in (rec["license"] or "").lower() for z in ["cc0","cc by","public domain"]):score+=4
      if rec["url"] and rec["sha1"]:score+=2
      if score>1: rec["score"]=score;recs.append(rec)
  recs.sort(key=lambda x:(-x["score"],x["title"] or ""))
  out[str(rid)]={"file_count":len(titles),"candidates":recs[:30]}
  print("TARGET",rid,"FILES",len(titles),"TOP",[(x["score"],x["title"],x["license"]) for x in recs[:12]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
