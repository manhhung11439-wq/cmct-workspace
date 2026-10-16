import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_fresh_harvest_109_124"); OUT.mkdir(parents=True,exist_ok=True)
targets={
109:{"taxon":"Terminalia catappa","terms":["Terminalia catappa detached leaves","Terminalia catappa harvested leaves","Terminalia catappa dried leaves"],"role":["leaf","leaves","detached","harvested","dried"]},
110:{"taxon":"Mangifera indica","terms":["Mangifera indica detached leaves","mango leaves harvested","mango leaves bunch","Mangifera indica dried leaves medicinal"],"role":["leaf","leaves","detached","harvested","dried"]},
111:{"taxon":"Annona muricata","terms":["Annona muricata detached leaves","soursop leaves harvested","Annona muricata dried leaves medicinal"],"role":["leaf","leaves","detached","harvested","dried"]},
114:{"taxon":"Gynura procumbens","terms":["Gynura procumbens harvested leaves young stems","Gynura procumbens fresh vegetable bunch","Gynura procumbens detached leaves","longevity spinach harvested leaves"],"role":["leaf","leaves","stem","harvested","detached","fresh","vegetable"]},
118:{"taxon":"Barleria lupulina","terms":["Barleria lupulina harvested leaves twigs","Barleria lupulina detached leaves","Barleria lupulina medicinal leaves"],"role":["leaf","leaves","twig","harvested","detached","medicinal"]},
121:{"taxon":"Phyllanthus acidus","terms":["Phyllanthus acidus harvested leaves fruit","Phyllanthus acidus detached leaves","star gooseberry leaves harvested"],"role":["leaf","leaves","fruit","harvested","detached"]},
124:{"taxon":"Clinacanthus nutans","terms":["Clinacanthus nutans harvested leaves twigs","Clinacanthus nutans detached leaves","Clinacanthus nutans medicinal leaves"],"role":["leaf","leaves","twig","harvested","detached","medicinal"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.7 harvested material search"
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
    seen={}; queries=[]
    for term in t["terms"]:
        data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":30,
                  "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,
                  "format":"json","formatversion":2})
        pages=data.get("query",{}).get("pages",[]); queries.append({"term":term,"count":len(pages)})
        for p in pages:
            ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
            def e(k): return clean(em.get(k) or "")
            title=p.get("title") or ""
            seen[title]={"title":title,"url":ii.get("url"),"thumburl":ii.get("thumburl"),"sha1":ii.get("sha1"),
                         "width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size"),
                         "license":e("LicenseShortName"),"license_url":e("LicenseUrl"),"author":e("Artist"),
                         "credit":e("Credit"),"description":e("ImageDescription"),"categories":e("Categories")}
        time.sleep(.4)
    def score(x):
        blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=0
        if t["taxon"].lower() in blob: sc+=12
        for z in t["role"]:
            if z.lower() in blob: sc+=4
        if any(z in blob for z in ["market","bunch","bundle","food","vegetable","herbal","medicinal"]): sc+=5
        if any(z in blob for z in ["on tree","plant in","living plant","flowering plant","herbarium","pressed specimen","illustration","pdf","djvu"]): sc-=12
        lic=(x.get("license") or "").lower()
        if any(z in lic for z in ["cc0","cc by","public domain","no restrictions"]): sc+=5
        if x.get("url") and x.get("sha1"): sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    allout[str(rid)]={"target":t,"queries":queries,"candidates":vals[:50]}
    print(rid,t["taxon"],"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:70]) for v in vals[:15]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
