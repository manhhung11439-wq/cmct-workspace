import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_101_110"); OUT.mkdir(parents=True,exist_ok=True)
targets={
101:("Paris polyphylla",["Paris polyphylla dried rhizome","Paridis Rhizoma","重楼 中药","重樓 藥材"],["rhizome","dried","重楼","重樓","药材","藥材"]),
102:("Premna serratifolia",["Premna serratifolia fresh leaves harvested","Premna serratifolia dried leaves","vong cach leaves"],["leaf","leaves","fresh","dried","harvested"]),
103:("Tiliacora triandra",["Tiliacora triandra fresh leaves harvested","Tiliacora triandra leaves market","sương sâm leaves"],["leaf","leaves","fresh","harvested"]),
104:("Platostoma palustre",["Platostoma palustre dried herb","Mesona chinensis dried whole herb","仙草 干草 中药"],["aerial","whole plant","herb","dried","仙草"]),
105:("Peperomia pellucida",["Peperomia pellucida fresh whole plant harvested","Peperomia pellucida edible greens","rau càng cua harvested"],["whole plant","fresh","harvested","edible"]),
108:("Blumea lacera",["Blumea lacera fresh whole herb harvested","Blumea lacera dried herb medicinal","cải trời herb"],["aerial","whole plant","fresh","dried","harvested"]),
109:("Terminalia catappa",["Terminalia catappa harvested leaves","Terminalia catappa dried leaves medicinal","dried Indian almond leaves"],["leaf","leaves","fresh","dried","harvested"]),
110:("Mangifera indica",["Mangifera indica harvested leaves","mango leaves bunch","dried mango leaves medicinal"],["leaf","leaves","fresh","dried","harvested"]),
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/2.0 targeted T1 M5 101-110"
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
    if isinstance(v,dict):v=v.get("value") or ""
    v=html.unescape(str(v or ""));v=re.sub(r"<[^>]+>"," ",v);return " ".join(v.split())
for rid,(taxon,terms,roles) in targets.items():
    seen={}
    for term in terms:
        data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":30,
                  "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,
                  "format":"json","formatversion":2})
        for p in data.get("query",{}).get("pages",[]):
            ii=(p.get("imageinfo") or [{}])[0];em=ii.get("extmetadata") or {}
            def e(k):return clean(em.get(k) or "")
            title=p.get("title") or ""
            seen[title]={"title":title,"url":ii.get("url"),"thumburl":ii.get("thumburl"),"sha1":ii.get("sha1"),
                         "width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size"),
                         "license":e("LicenseShortName"),"license_url":e("LicenseUrl"),"author":e("Artist"),
                         "credit":e("Credit"),"description":e("ImageDescription"),"categories":e("Categories")}
        time.sleep(.45)
    def score(x):
        blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=(12 if taxon.lower() in blob else 0)+sum(4 for z in roles if z.lower() in blob)
        if any(z in blob for z in ["herbal medicine","medicinal","market","food","edible","crude drug"]):sc+=5
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu","growing plant","habitus"]):sc-=12
        if any(z in (x.get("license") or "").lower() for z in ["cc0","cc by","public domain","no restrictions"]):sc+=5
        if x.get("url") and x.get("sha1"):sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
    (OUT/f"{rid}.json").write_text(json.dumps(vals[:40],ensure_ascii=False,indent=2),encoding="utf-8")
