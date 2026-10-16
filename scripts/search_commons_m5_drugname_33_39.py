import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_drugname_33_39"); OUT.mkdir(parents=True,exist_ok=True)
targets={
33:{"taxon":"Paeonia suffruticosa","terms":["牡丹皮 中藥","牡丹皮 藥材","Moutan Cortex","Paeonia suffruticosa dried root bark"],"role":["root bark","cortex","dried","牡丹皮","藥材","药材"]},
34:{"taxon":"Solanum procumbens","terms":["Solanum procumbens dried herb medicinal","Cà gai leo dried medicinal herb","Solanum procumbens stems roots dried"],"role":["dried","herb","stem","root","medicinal"]},
35:{"taxon":"Cynara scolymus","terms":["Cynara scolymus dried leaves","artichoke dried leaves medicinal","Cynara cardunculus leaf drug"],"role":["leaf","leaves","dried","medicinal"]},
36:{"taxon":"Phyllanthus urinaria","terms":["Phyllanthus urinaria dried whole herb","Phyllanthus urinaria medicinal herb","Diệp hạ châu dried herb"],"role":["whole","herb","dried","medicinal"]},
37:{"taxon":"Gymnema sylvestre","terms":["Gymnema sylvestre dried leaves","Gymnema leaves medicinal material","Gymnemae Folium"],"role":["leaf","leaves","dried","medicinal"]},
38:{"taxon":"Celastrus hindsii","terms":["Celastrus hindsii dried leaves stems","xạ đen dried medicinal herb","Celastrus hindsii medicinal material"],"role":["leaf","leaves","stem","dried","medicinal"]},
39:{"taxon":"Hedyotis diffusa","terms":["白花蛇舌草 中藥","白花蛇舌草 藥材","Hedyotis diffusa dried herb","Scleromitrion diffusum dried herb"],"role":["herb","whole","dried","白花蛇舌草","藥材","药材"]},
}
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/1.6 drugname 33-39"
api="https://commons.wikimedia.org/w/api.php"
def get(params):
  last=None
  for i in range(8):
    r=s.get(api,params=params,timeout=90);last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(int(r.headers.get("Retry-After") or min(60,3*(2**i))));continue
    r.raise_for_status();return r.json()
  last.raise_for_status()
def clean(v):
  if isinstance(v,dict):v=v.get("value") or ""
  v=html.unescape(str(v or ""));v=re.sub(r"<[^>]+>"," ",v)
  return " ".join(v.split())
out={}
for rid,t in targets.items():
  seen={};qs=[]
  for term in t["terms"]:
    data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":40,
      "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,"format":"json","formatversion":2})
    pages=data.get("query",{}).get("pages",[]);qs.append({"term":term,"count":len(pages)})
    for p in pages:
      ii=(p.get("imageinfo") or [{}])[0];em=ii.get("extmetadata") or {}
      def e(k):return clean(em.get(k) or "")
      title=p.get("title") or ""
      seen[title]={"title":title,"url":ii.get("url"),"sha1":ii.get("sha1"),"size":ii.get("size"),
        "width":ii.get("width"),"height":ii.get("height"),"license":e("LicenseShortName"),
        "license_url":e("LicenseUrl"),"author":e("Artist"),"credit":e("Credit"),
        "description":e("ImageDescription"),"categories":e("Categories")}
    time.sleep(.55)
  def score(x):
    blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
    sc=12 if t["taxon"].lower() in blob else 0
    sc+=sum(4 for z in t["role"] if z.lower() in blob)
    if any(z in blob for z in ["herbal medicine","chinese medicine","crude drug","materia medica","medicinal","中藥","中药"]):sc+=8
    if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu","living plant"]):sc-=15
    lic=(x.get("license") or "").lower()
    if any(z in lic for z in ["cc0","cc by","public domain"]):sc+=5
    if x.get("url") and x.get("sha1"):sc+=2
    return sc
  vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
  for x in vals:x["score"]=score(x)
  out[str(rid)]={"target":t,"queries":qs,"candidates":vals[:50]}
  print("TARGET",rid,t["taxon"],"UNIQUE",len(vals),"TOP",[(v["score"],v["title"],v["license"],v["description"][:100]) for v in vals[:12]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
