import json,time,re,html
from pathlib import Path
import requests

OUT=Path("evidence/m5_t1_target_43_48"); OUT.mkdir(parents=True,exist_ok=True)
targets={
 43:{"taxon":"Scutellaria baicalensis","terms":["Scutellaria baicalensis dried root","Scutellariae Radix","Huangqin dried root","黄芩 中药","黃芩 藥材"],"role":["root","radix","dried","黄芩","藥材","药材"]},
 44:{"taxon":"Coptis chinensis","terms":["Coptis chinensis dried rhizome","Coptidis Rhizoma","Huanglian dried rhizome","黄连 中药","黃連 藥材"],"role":["rhizome","dried","coptidis","黄连","黃連","藥材","药材"]},
 45:{"taxon":"Phellodendron chinense","terms":["Phellodendron chinense dried bark","Phellodendri Chinensis Cortex","Chuan huang bai bark","黄柏 中药","川黄柏 藥材"],"role":["bark","cortex","dried","黄柏","川黄柏","藥材","药材"]},
 47:{"taxon":"Forsythia suspensa","terms":["Forsythia suspensa dried fruit","Forsythiae Fructus","Lianqiao dried fruit","连翘 中药","連翹 藥材"],"role":["fruit","fructus","dried","连翘","連翹","藥材","药材"]},
 48:{"taxon":"Gardenia jasminoides","terms":["Gardenia jasminoides dried fruit","Gardeniae Fructus","Zhizi dried fruit","栀子 中药","梔子 藥材"],"role":["fruit","fructus","dried","栀子","梔子","藥材","药材"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.4 targeted crude-drug search"
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
        time.sleep(.5)
    def score(x):
        blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=0
        if t["taxon"].lower() in blob: sc+=12
        for z in t["role"]:
            if z.lower() in blob: sc+=4
        if any(z in blob for z in ["herbal medicine","chinese medicine","materia medica","medicinal"]): sc+=6
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut","pdf","djvu"]): sc-=12
        lic=(x.get("license") or "").lower()
        if any(z in lic for z in ["cc0","cc by","public domain","no restrictions"]): sc+=5
        if x.get("url") and x.get("sha1"): sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    allout[str(rid)]={"target":t,"queries":queries,"candidates":vals[:40]}
    print(rid,t["taxon"],"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
