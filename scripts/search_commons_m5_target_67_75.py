import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_67_75"); OUT.mkdir(parents=True,exist_ok=True)
targets={
67:{"taxon":"Sphagneticola calendulacea","terms":["Sphagneticola calendulacea harvested whole plant","Wedelia chinensis fresh herb","Sài đất dried herb"],"role":["whole plant","herb","fresh","dried","harvest"]},
68:{"taxon":"Phyllostachys nigra","terms":["Phyllostachys nigra young leaves harvested","bamboo young leaves medicinal","竹葉 dried leaves"],"role":["leaf","leaves","young","fresh","dried"]},
69:{"taxon":"Lophatherum gracile","terms":["Lophatherum gracile dried whole herb","Lophatheri Herba","淡竹葉 中药","淡竹葉 藥材"],"role":["whole plant","herb","dried","淡竹葉","藥材","药材"]},
70:{"taxon":"Sophora flavescens","terms":["Sophora flavescens dried root slices","Sophorae Flavescentis Radix","苦参 中药","苦參 藥材"],"role":["root","radix","dried","slice","苦参","苦參"]},
71:{"taxon":"Dictamnus dasycarpus","terms":["Dictamnus dasycarpus dried root bark","Dictamni Cortex","白鮮皮 中药","白鲜皮 药材"],"role":["root bark","cortex","dried","白鮮皮","白鲜皮"]},
72:{"taxon":"Fraxinus rhynchophylla","terms":["Fraxinus rhynchophylla dried bark","Fraxini Cortex","秦皮 中药","秦皮 藥材"],"role":["bark","cortex","dried","秦皮"]},
73:{"taxon":"Viola yedoensis","terms":["Viola yedoensis harvested whole plant","Violae Herba dried","紫花地丁 中药","紫花地丁 藥材"],"role":["whole plant","herb","fresh","dried","紫花地丁"]},
74:{"taxon":"Isatis tinctoria","terms":["Isatis tinctoria dried leaves","Isatidis Folium","大青葉 中药","大青叶 药材"],"role":["leaf","leaves","dried","大青葉","大青叶"]},
75:{"taxon":"Strobilanthes cusia","terms":["Indigo Naturalis medicinal powder","Qing Dai medicinal indigo powder","青黛 中药","青黛 藥材","Strobilanthes cusia indigo medicinal"],"role":["powder","indigo","naturalis","青黛","medicinal"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.7 targeted medicinal-material search"
api="https://commons.wikimedia.org/w/api.php"
def get(params):
  last=None
  for i in range(8):
    r=s.get(api,params=params,timeout=90); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(int(r.headers.get("Retry-After") or min(60,3*(2**i)))); continue
    r.raise_for_status(); return r.json()
  last.raise_for_status()
def clean(v):
  if isinstance(v,dict): v=v.get("value") or ""
  v=html.unescape(str(v or "")); v=re.sub(r"<[^>]+>"," ",v)
  return " ".join(v.split())
allout={}
for rid,t in targets.items():
  seen={};qs=[]
  for term in t["terms"]:
    data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":30,
              "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,
              "format":"json","formatversion":2})
    pages=data.get("query",{}).get("pages",[]); qs.append({"term":term,"count":len(pages)})
    for p in pages:
      ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
      def e(k): return clean(em.get(k) or "")
      title=p.get("title") or ""
      seen[title]={"title":title,"url":ii.get("url"),"sha1":ii.get("sha1"),"width":ii.get("width"),
                   "height":ii.get("height"),"size":ii.get("size"),"license":e("LicenseShortName"),
                   "license_url":e("LicenseUrl"),"author":e("Artist"),"credit":e("Credit"),
                   "description":e("ImageDescription"),"categories":e("Categories")}
    time.sleep(.45)
  def score(x):
    blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
    sc=12 if t["taxon"].lower() in blob else 0
    sc+=sum(4 for z in t["role"] if z.lower() in blob)
    if any(z in blob for z in ["medicinal","herbal medicine","chinese medicine","materia medica","crude drug"]): sc+=7
    if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut","pdf","djvu","living plant","flowering plant"]): sc-=12
    lic=(x.get("license") or "").lower()
    if any(z in lic for z in ["cc0","cc by","public domain","no restrictions"]): sc+=5
    if x.get("url") and x.get("sha1"): sc+=2
    return sc
  vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
  for x in vals:x["score"]=score(x)
  allout[str(rid)]={"target":t,"queries":qs,"candidates":vals[:50]}
  print(rid,t["taxon"],"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
