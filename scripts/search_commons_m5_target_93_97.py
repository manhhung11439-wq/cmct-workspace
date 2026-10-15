import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_93_97"); OUT.mkdir(parents=True,exist_ok=True)
targets={
93:("Bidens pilosa",["Bidens pilosa harvested aerial herb","Bidens pilosa dried herb medicinal","Bidens pilosa fresh herb"],["aerial","herb","fresh","dried","harvested"]),
94:("Pulsatilla chinensis",["Pulsatilla chinensis dried root","Pulsatillae Radix","白头翁 中药","白頭翁 藥材"],["root","radix","dried","白头翁","白頭翁","药材","藥材"]),
95:("Sophora tonkinensis",["Sophora tonkinensis dried root rhizome","Sophorae Tonkinensis Radix et Rhizoma","山豆根 中药","山豆根 藥材"],["root","rhizome","radix","dried","山豆根","药材","藥材"]),
96:("Lasiosphaera fenzlii",["Lasiosphaera fenzlii dried fruiting body","Calvatia gigantea medicinal dried puffball","Lasiosphaera puffball Chinese medicine","马勃 中药","馬勃 藥材"],["fruiting body","spore","puffball","dried","马勃","馬勃","药材","藥材"]),
97:("Lobelia chinensis",["Lobelia chinensis dried whole herb","Lobeliae Chinensis Herba","半边莲 中药","半邊蓮 藥材"],["whole herb","herb","dried","半边莲","半邊蓮","药材","藥材"]),
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.9 targeted T1 M5 93-97"
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
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu","growing plant","habitus"]):sc-=12
        if any(z in (x.get("license") or "").lower() for z in ["cc0","cc by","public domain","no restrictions"]):sc+=5
        if x.get("url") and x.get("sha1"):sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
    (OUT/f"{rid}.json").write_text(json.dumps(vals[:40],ensure_ascii=False,indent=2),encoding="utf-8")
