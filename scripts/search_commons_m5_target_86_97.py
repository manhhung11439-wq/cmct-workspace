# resume marker 2026-10-16T15:12+07 — parallel target 86-97 from promoted REV17
import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_86_97"); OUT.mkdir(parents=True,exist_ok=True)
targets={
86:{"taxon":"Catharanthus roseus","terms":["Catharanthus roseus dried whole herb","Catharanthi rosei Herba","Catharanthus roseus dried root medicinal"],"role":["whole herb","herba","root","dried","medicinal"]},
87:{"taxon":"Gymnanthemum amygdalinum","terms":["Gymnanthemum amygdalinum harvested leaves","Vernonia amygdalina dried leaves","bitter leaf harvested medicinal"],"role":["leaf","leaves","harvested","dried","medicinal"]},
88:{"taxon":"Jasminum subtriplinerve","terms":["Jasminum subtriplinerve dried stems leaves","chè vằng dried herb","Jasmini subtriplinervis herba"],"role":["stem","leaf","leaves","dried","herb"]},
89:{"taxon":"Excoecaria cochinchinensis","terms":["Excoecaria cochinchinensis dried leaves twigs","Folium Excoecariae dried","đơn lá đỏ dried leaves"],"role":["leaf","leaves","twig","dried","folium"]},
90:{"taxon":"Sauropus androgynus","terms":["Sauropus androgynus harvested leaves","Sauropus androgynus fresh leaves market","Sauropus androgynus dried root"],"role":["leaf","leaves","root","fresh","dried","harvested"]},
91:{"taxon":"Nelumbo nucifera","terms":["Nelumbo nucifera dried leaf medicinal","Nelumbinis Folium","lotus dried leaf tea Nelumbo nucifera","荷葉 中藥"],"role":["leaf","folium","dried","lotus","荷葉","medicinal"]},
92:{"taxon":"Eleusine indica","terms":["Eleusine indica harvested whole plant roots","Eleusine indica dried whole herb","goosegrass harvested medicinal"],"role":["whole plant","root","herb","fresh","dried","harvested"]},
93:{"taxon":"Bidens pilosa","terms":["Bidens pilosa harvested aerial parts","Bidens pilosa dried herb medicinal","Herba Bidentis pilosae"],"role":["aerial","herb","fresh","dried","harvested"]},
94:{"taxon":"Pulsatilla chinensis","terms":["Pulsatilla chinensis dried root","Pulsatillae Radix","Baitouweng dried root","白頭翁 中藥","白头翁 药材"],"role":["root","radix","dried","白頭翁","白头翁","medicinal"]},
95:{"taxon":"Sophora tonkinensis","terms":["Sophora tonkinensis dried root rhizome","Sophorae Tonkinensis Radix et Rhizoma","Shandougen dried root","山豆根 中藥","山豆根 药材"],"role":["root","rhizome","radix","dried","山豆根","medicinal"]},
96:{"taxon":"Lasiosphaera fenzlii","terms":["Lasiosphaera fenzlii dried puffball medicinal","Calvatia gigantea dried puffball medicinal","Lasiosphaera Calvatia Mabo Chinese medicine","馬勃 中藥"],"role":["puffball","fruiting body","spore","dried","馬勃","medicinal"]},
97:{"taxon":"Lobelia chinensis","terms":["Lobelia chinensis dried whole herb","Lobeliae Chinensis Herba","Banbianlian dried herb","半邊蓮 中藥","半边莲 药材"],"role":["whole herb","herba","dried","半邊蓮","半边莲","medicinal"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.9 targeted M5 86-97"
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
    seen={};qs=[]
    for term in t["terms"]:
        data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":30,
                  "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,
                  "format":"json","formatversion":2})
        pages=data.get("query",{}).get("pages",[]);qs.append({"term":term,"count":len(pages)})
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
        sc=12 if t["taxon"].lower() in blob else 0
        sc+=sum(4 for z in t["role"] if z.lower() in blob)
        if any(z in blob for z in ["medicinal","herbal medicine","chinese medicine","materia medica","crude drug"]): sc+=7
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut","pdf","djvu","living plant","flowering plant"]): sc-=12
        lic=(x.get("license") or "").lower()
        if any(z in lic for z in ["cc0","cc by","public domain","no restrictions"]): sc+=5
        if x.get("url") and x.get("sha1"): sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    allout[str(rid)]={"target":t,"queries":qs,"candidates":vals[:50]}
    print(rid,t["taxon"],"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:70]) for v in vals[:15]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
