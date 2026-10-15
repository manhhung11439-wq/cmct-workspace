import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_67_75"); OUT.mkdir(parents=True,exist_ok=True)
targets={
67:("Sphagneticola calendulacea",["Sphagneticola calendulacea harvested whole plant","Wedelia chinensis dried herb","Sphagneticola calendulacea fresh herb"],["whole plant","herb","fresh","dried","harvested"]),
68:("Phyllostachys nigra",["Phyllostachys nigra young leaves","Phyllostachys nigra dried leaves","bamboo young leaves medicinal"],["leaf","leaves","young","fresh","dried"]),
69:("Lophatherum gracile",["Lophatherum gracile dried herb","Lophatheri Herba","淡竹叶 中药","淡竹葉 藥材"],["herb","whole plant","dried","淡竹叶","淡竹葉","药材","藥材"]),
70:("Sophora flavescens",["Sophora flavescens dried root slices","Sophorae Flavescentis Radix","苦参 中药","苦參 藥材"],["root","radix","slice","dried","苦参","苦參","药材","藥材"]),
71:("Dictamnus dasycarpus",["Dictamnus dasycarpus dried root bark","Dictamni Cortex","白鲜皮 中药","白鮮皮 藥材"],["root bark","cortex","dried","白鲜皮","白鮮皮","药材","藥材"]),
72:("Fraxinus rhynchophylla",["Fraxinus rhynchophylla dried bark","Fraxini Cortex","秦皮 中药","秦皮 藥材"],["bark","cortex","dried","秦皮","药材","藥材"]),
73:("Viola yedoensis",["Viola yedoensis harvested whole plant","Violae Herba dried","紫花地丁 中药","紫花地丁 藥材"],["whole plant","herb","fresh","dried","紫花地丁","药材","藥材"]),
74:("Isatis tinctoria",["Isatis tinctoria dried leaves","Isatidis Folium","大青叶 中药","大青葉 藥材"],["leaf","leaves","folium","dried","大青叶","大青葉","药材","藥材"]),
75:("Strobilanthes cusia",["Indigo Naturalis medicinal powder","Qing Dai Indigo Naturalis","青黛 中药 粉末","Strobilanthes cusia indigo powder"],["indigo naturalis","powder","青黛","medicinal","ferment","lime"]),
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.7 targeted T1 M5 67-75"
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
        if any(z in blob for z in ["herbal medicine","chinese medicine","medicinal","crude drug"]):sc+=6
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu"]):sc-=12
        if any(z in (x.get("license") or "").lower() for z in ["cc0","cc by","public domain","no restrictions"]):sc+=5
        if x.get("url") and x.get("sha1"):sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
    (OUT/f"{rid}.json").write_text(json.dumps(vals[:40],ensure_ascii=False,indent=2),encoding="utf-8")
