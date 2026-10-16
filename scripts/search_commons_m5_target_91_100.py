import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_91_100"); OUT.mkdir(parents=True,exist_ok=True)
targets={
91:{"taxon":"Nelumbo nucifera","terms":["Nelumbo nucifera dried leaf herbal medicine","Nelumbinis Folium dried","He Ye lotus leaf dried Chinese medicine","荷叶 中药材","荷葉 藥材"],"role":["leaf","folium","dried","荷叶","荷葉","herbal medicine","藥材","药材"]},
92:{"taxon":"Eleusine indica","terms":["Eleusine indica harvested whole plant medicinal","Eleusine indica dried whole herb","goosegrass medicinal herb roots"],"role":["whole plant","herb","root","harvested","dried","medicinal"]},
93:{"taxon":"Bidens pilosa","terms":["Bidens pilosa harvested aerial herb medicinal","Bidens pilosa dried herb","fresh harvested Bidens pilosa"],"role":["aerial","herb","harvested","dried","fresh","medicinal"]},
94:{"taxon":"Pulsatilla chinensis","terms":["Pulsatilla chinensis dried root","Pulsatillae Radix","Baitouweng dried root","白头翁 中药材","白頭翁 藥材"],"role":["root","radix","dried","白头翁","白頭翁","藥材","药材"]},
95:{"taxon":"Sophora tonkinensis","terms":["Sophora tonkinensis dried root rhizome","Sophorae Tonkinensis Radix et Rhizoma","Shandougen dried root","山豆根 中药材","山豆根 藥材"],"role":["root","rhizome","radix","dried","山豆根","藥材","药材"]},
96:{"taxon":"Calvatia","terms":["Calvatia dried puffball medicinal","Lasiosphaera puffball dried medicine","Lasiosphaera seu Calvatia medicinal","马勃 中药材","馬勃 藥材"],"role":["puffball","fruiting body","spore","dried","马勃","馬勃","medicinal"]},
97:{"taxon":"Lobelia chinensis","terms":["Lobelia chinensis dried whole herb","Lobeliae Chinensis Herba","Banbianlian dried herb","半边莲 中药材","半邊蓮 藥材"],"role":["whole herb","herba","dried","半边莲","半邊蓮","藥材","药材"]},
100:{"taxon":"Kalanchoe pinnata","terms":["Kalanchoe pinnata detached fresh leaves","Kalanchoe pinnata harvested leaves","Bryophyllum pinnatum fresh leaves medicinal"],"role":["leaf","leaves","detached","harvested","fresh","medicinal"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.6 targeted crude-drug search"
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
        time.sleep(.45)
    def score(x):
        blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=0
        if t["taxon"].lower() in blob: sc+=12
        for z in t["role"]:
            if z.lower() in blob: sc+=4
        if any(z in blob for z in ["herbal medicine","chinese medicine","materia medica","medicinal","crude drug"]): sc+=7
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut","pdf","djvu","living plant","flowering plant"]): sc-=12
        lic=(x.get("license") or "").lower()
        if any(z in lic for z in ["cc0","cc by","public domain","no restrictions"]): sc+=5
        if x.get("url") and x.get("sha1"): sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    allout[str(rid)]={"target":t,"queries":queries,"candidates":vals[:50]}
    print(rid,t["taxon"],"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:70]) for v in vals[:15]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
