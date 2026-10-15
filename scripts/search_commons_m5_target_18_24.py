import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_18_24"); OUT.mkdir(parents=True,exist_ok=True)
targets={
18:("Actaea cimicifuga",["Actaea cimicifuga dried rhizome","Cimicifuga foetida dried rhizome","Cimicifugae Rhizoma","升麻 中药","升麻 藥材"],["rhizome","dried","升麻","药材","藥材"]),
21:("Elsholtzia ciliata",["Elsholtzia ciliata dried aerial herb","Elsholtziae Herba","香薷 中药","香薷 藥材"],["aerial","herb","dried","香薷","药材","藥材"]),
22:("Centipeda minima",["Centipeda minima dried herb","Centipedae Herba","鹅不食草 中药","鵝不食草 藥材"],["herb","whole plant","dried","鹅不食草","鵝不食草","药材","藥材"]),
23:("Vitex trifolia",["Vitex trifolia dried ripe fruit","Viticis Fructus","蔓荆子 中药","蔓荊子 藥材"],["fruit","fructus","dried","蔓荆子","蔓荊子","药材","藥材"]),
24:("Spirodela polyrhiza",["Spirodela polyrhiza dried herb medicinal","Spirodelae Herba","浮萍 中药","浮萍 藥材"],["herb","whole plant","dried","浮萍","药材","藥材"]),
}
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/2.3 targeted T1 M5 18-24"
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
    v=html.unescape(str(v or ""));v=re.sub(r"<[^>]+>"," ",v);return " ".join(v.split())
for rid,(taxon,terms,roles) in targets.items():
    seen={}
    for term in terms:
        data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":30,"prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,"format":"json","formatversion":2})
        for p in data.get("query",{}).get("pages",[]):
            ii=(p.get("imageinfo") or [{}])[0];em=ii.get("extmetadata") or {}
            def e(k):return clean(em.get(k) or "")
            title=p.get("title") or ""
            seen[title]={"title":title,"url":ii.get("url"),"sha1":ii.get("sha1"),"width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size"),"license":e("LicenseShortName"),"license_url":e("LicenseUrl"),"author":e("Artist"),"credit":e("Credit"),"description":e("ImageDescription"),"categories":e("Categories")}
        time.sleep(.45)
    def score(x):
        blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=(12 if taxon.lower() in blob else 0)+sum(4 for z in roles if z.lower() in blob)
        if any(z in blob for z in ["herbal medicine","chinese medicine","medicinal","crude drug"]):sc+=6
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu","growing plant","habitus"]):sc-=12
        if any(z in (x.get("license") or "").lower() for z in ["cc0","cc by","public domain","no restrictions"]):sc+=5
        if x.get("url") and x.get("sha1"):sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
    (OUT/f"{rid}.json").write_text(json.dumps(vals[:40],ensure_ascii=False,indent=2),encoding="utf-8")
