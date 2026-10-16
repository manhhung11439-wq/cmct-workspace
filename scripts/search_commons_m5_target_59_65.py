# resume marker 2026-10-16T15:12+07 — parallel target 59-65
import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_59_65"); OUT.mkdir(parents=True,exist_ok=True)
targets={
59:{"taxon":"Callisia fragrans","terms":["Callisia fragrans harvested stems leaves","Callisia fragrans cut stems leaves","Callisia fragrans dried herb medicinal"],"role":["harvested","stems","leaves","dried","cut"]},
60:{"taxon":"Pseuderanthemum palatiferum","terms":["Pseuderanthemum palatiferum harvested leaves","Pseuderanthemum palatiferum fresh leaves","Pseuderanthemum palatiferum dried leaves"],"role":["leaves","fresh","harvested","dried"]},
61:{"taxon":"Helicteres hirsuta","terms":["Helicteres hirsuta dried stems leaves medicine","Helicteres hirsuta roasted herb","An xoa dried herb"],"role":["stems","leaves","dried","roasted","medicine"]},
62:{"taxon":"Paederia lanuginosa","terms":["Paederia lanuginosa fresh leaves harvested","Paederia lanuginosa picked leaves","Paederia lanuginosa leaves food"],"role":["fresh","leaves","harvested","picked","food"]},
63:{"taxon":"Ampelopsis cantoniensis","terms":["Ampelopsis cantoniensis dried stems leaves","Ampelopsis cantoniensis dried herb","vine tea Ampelopsis cantoniensis"],"role":["dried","stems","leaves","tea","herb"]},
64:{"taxon":"Hedyotis capitellata","terms":["Hedyotis capitellata dried stems leaves","Hedyotis capitellata dried herb","Da cam medicinal herb"],"role":["dried","stems","leaves","herb","medicinal"]},
65:{"taxon":"Crinum latifolium","terms":["Crinum latifolium sliced dried leaves","Crinum latifolium roasted leaves","Crinum latifolium medicinal leaves"],"role":["leaves","sliced","roasted","dried","medicinal"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.7 target-59-65"
api="https://commons.wikimedia.org/w/api.php"
def clean(v):
  if isinstance(v,dict): v=v.get("value") or ""
  v=html.unescape(str(v or "")); v=re.sub(r"<[^>]+>"," ",v); return " ".join(v.split())
def get(params):
  last=None
  for i in range(7):
    r=s.get(api,params=params,timeout=90); last=r
    if r.status_code in (429,500,502,503,504): time.sleep(int(r.headers.get("Retry-After") or min(45,3*(2**i)))); continue
    r.raise_for_status(); return r.json()
  last.raise_for_status()
allout={}
for rid,t in targets.items():
  seen={}
  for term in t["terms"]:
    data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":35,
              "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,"format":"json","formatversion":2})
    for p in data.get("query",{}).get("pages",[]):
      ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
      def e(k): return clean(em.get(k) or "")
      title=p.get("title") or ""
      seen[title]={"title":title,"url":ii.get("url"),"sha1":ii.get("sha1"),"width":ii.get("width"),"height":ii.get("height"),
                   "license":e("LicenseShortName"),"license_url":e("LicenseUrl"),"author":e("Artist"),"credit":e("Credit"),
                   "description":e("ImageDescription"),"categories":e("Categories")}
    time.sleep(.5)
  def score(x):
    blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower(); sc=0
    if t["taxon"].lower() in blob: sc+=12
    sc+=sum(4 for z in t["role"] if z.lower() in blob)
    if any(z in blob for z in ["herbal medicine","medicinal","food","market","harvest"]): sc+=5
    if any(z in blob for z in ["herbarium","pressed specimen","illustration","pdf","djvu","living plant","habitus"]): sc-=12
    lic=(x.get("license") or "").lower()
    if any(z in lic for z in ["cc0","cc by","public domain"]): sc+=5
    if x.get("url") and x.get("sha1"): sc+=2
    return sc
  vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
  for x in vals:x["score"]=score(x)
  allout[str(rid)]={"target":t,"candidates":vals[:50]}
  print(rid,t["taxon"],"unique",len(vals),"top",[(v["score"],v["title"],v["license"]) for v in vals[:12]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
