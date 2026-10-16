import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_59_65"); OUT.mkdir(parents=True,exist_ok=True)
targets={
59:{"taxon":"Callisia fragrans","terms":["Callisia fragrans harvested stems leaves","Callisia fragrans dried herb","Callisia fragrans medicinal herb"],"role":["stem","leaf","leaves","herb","dried","harvest"]},
60:{"taxon":"Pseuderanthemum palatiferum","terms":["Pseuderanthemum palatiferum fresh leaves","Pseuderanthemum palatiferum dried leaves","Pseuderanthemum palatiferum medicinal leaves"],"role":["leaf","leaves","fresh","dried","harvest"]},
61:{"taxon":"Helicteres hirsuta","terms":["Helicteres hirsuta dried stems leaves","Helicteres hirsuta medicinal herb","An xoa sao vang dried"],"role":["stem","branch","leaf","leaves","dried","roasted","sao"]},
62:{"taxon":"Paederia lanuginosa","terms":["Paederia lanuginosa fresh leaves","Paederia lanuginosa picked leaves","Paederia lanuginosa medicinal leaf"],"role":["leaf","leaves","fresh","picked","harvest"]},
63:{"taxon":"Ampelopsis cantoniensis","terms":["Ampelopsis cantoniensis dried stems leaves","Ampelopsis cantoniensis medicinal tea","chè dây dried"],"role":["stem","leaf","leaves","dried","tea","herb"]},
64:{"taxon":"Hedyotis capitellata","terms":["Hedyotis capitellata dried stems leaves","Hedyotis capitellata medicinal herb","dạ cẩm dried"],"role":["stem","leaf","leaves","dried","herb"]},
65:{"taxon":"Crinum latifolium","terms":["Crinum latifolium dried leaves","Crinum latifolium roasted leaves","Trinh nu hoang cung dried sliced leaves"],"role":["leaf","leaves","dried","roasted","sliced"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.6 targeted medicinal-material search"
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
  seen={}; qs=[]
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
    if any(z in blob for z in ["medicinal","herbal medicine","materia medica","tea","food","market"]): sc+=5
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
