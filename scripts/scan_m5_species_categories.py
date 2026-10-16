# CMCT T1 exact-species-category processed material scan — 2026-10-16
import json,time,re,html
from pathlib import Path
import requests

OUT=Path("evidence/m5_t1_species_category_scan"); OUT.mkdir(parents=True,exist_ok=True)
targets={
43:{"cats":["Scutellaria baicalensis"],"good":["root","radix","dried","drug","medicine","herbal","黄芩","黃芩","药材","藥材"]},
44:{"cats":["Coptis chinensis"],"good":["rhizome","dried","drug","medicine","herbal","黄连","黃連","药材","藥材"]},
47:{"cats":["Forsythia suspensa"],"good":["fruit","fructus","dried","drug","medicine","连翘","連翹","药材","藥材"]},
48:{"cats":["Gardenia jasminoides"],"good":["fruit","fructus","dried","drug","medicine","栀子","梔子","药材","藥材"]},
51:{"cats":["Gentiana scabra"],"good":["root","rhizome","radix","dried","drug","龍膽","龙胆","药材","藥材"]},
53:{"cats":["Isatis tinctoria"],"good":["root","radix","dried","drug","板蓝根","板藍根","药材","藥材"]},
54:{"cats":["Iris domestica","Belamcanda chinensis"],"good":["rhizome","dried","drug","射干","药材","藥材"]},
55:{"cats":["Paeonia lactiflora"],"good":["root","radix","dried","slice","赤芍","drug","药材","藥材"]},
56:{"cats":["Lycium chinense"],"good":["root bark","bark","cortex","dried","地骨皮","drug","药材","藥材"]},
57:{"cats":["Artemisia annua"],"good":["dried","dry","herb","aerial","drug","青蒿","药材","藥材"]},
58:{"cats":["Andrographis paniculata"],"good":["dried","dry","herb","aerial","cut","drug","穿心莲","穿心蓮","药材","藥材"]},
70:{"cats":["Sophora flavescens"],"good":["root","radix","dried","slice","苦参","苦參","drug","药材","藥材"]},
71:{"cats":["Dictamnus dasycarpus"],"good":["root bark","cortex","dried","白鲜皮","白鮮皮","drug","药材","藥材"]},
72:{"cats":["Fraxinus rhynchophylla"],"good":["bark","cortex","dried","秦皮","drug","药材","藥材"]},
74:{"cats":["Isatis tinctoria"],"good":["leaf","folium","dried","cut","大青叶","大青葉","drug","药材","藥材"]},
75:{"cats":["Strobilanthes cusia"],"good":["indigo","powder","青黛","naturalis","drug","medicine","药材","藥材"]},
77:{"cats":["Lithospermum erythrorhizon"],"good":["root","radix","dried","紫草","drug","药材","藥材"]},
79:{"cats":["Picrorhiza scrophulariiflora"],"good":["rhizome","dried","胡黄连","胡黃連","drug","药材","藥材"]},
80:{"cats":["Cynanchum atratum"],"good":["root","rhizome","dried","白薇","drug","药材","藥材"]},
91:{"cats":["Nelumbo nucifera"],"good":["leaf","folium","dried","dry","荷叶","荷葉","drug","tea","药材","藥材"]},
94:{"cats":["Pulsatilla chinensis"],"good":["root","radix","dried","白头翁","白頭翁","drug","药材","藥材"]},
95:{"cats":["Sophora tonkinensis"],"good":["root","rhizome","dried","山豆根","drug","药材","藥材"]},
97:{"cats":["Lobelia chinensis"],"good":["whole","herb","dried","半边莲","半邊蓮","drug","药材","藥材"]},
101:{"cats":["Paris polyphylla"],"good":["rhizome","dried","重楼","重樓","drug","药材","藥材"]},
123:{"cats":["Scutellaria barbata"],"good":["whole","herb","dried","半枝莲","半枝蓮","drug","药材","藥材"]},
}
api="https://commons.wikimedia.org/w/api.php"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/2.1 exact species category processed-material scan"
def get(params):
    last=None
    for i in range(8):
        r=s.get(api,params=params,timeout=90); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(int(r.headers.get("Retry-After") or min(45,2*(2**i)))); continue
        r.raise_for_status(); return r.json()
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict):v=v.get("value") or ""
    return " ".join(re.sub(r"<[^>]+>"," ",html.unescape(str(v or ""))).split())
allout={}
for rid,t in targets.items():
    titles=set();catlog=[]
    for cat in t["cats"]:
        cont=None;n=0
        while True:
            p={"action":"query","list":"categorymembers","cmtitle":"Category:"+cat,"cmtype":"file","cmlimit":"500",
               "format":"json","formatversion":2}
            if cont:p["cmcontinue"]=cont
            d=get(p); vals=d.get("query",{}).get("categorymembers",[])
            for m in vals:titles.add(m["title"])
            n+=len(vals);cont=(d.get("continue") or {}).get("cmcontinue")
            if not cont:break
        catlog.append({"category":cat,"files":n})
    records=[]
    tl=sorted(titles)
    for i in range(0,len(tl),50):
        d=get({"action":"query","titles":"|".join(tl[i:i+50]),"prop":"imageinfo",
               "iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2})
        for p in d.get("query",{}).get("pages",[]):
            ii=(p.get("imageinfo") or [{}])[0];em=ii.get("extmetadata") or {};e=lambda k:clean(em.get(k) or "")
            rec={"title":p.get("title"),"url":ii.get("url"),"sha1":ii.get("sha1"),"size":ii.get("size"),
                 "width":ii.get("width"),"height":ii.get("height"),"license":e("LicenseShortName"),
                 "license_url":e("LicenseUrl"),"author":e("Artist"),"credit":e("Credit"),
                 "description":e("ImageDescription"),"categories":e("Categories")}
            blob=" ".join(str(rec.get(k) or "") for k in ("title","description","categories")).lower()
            score=sum(5 for z in t["good"] if z.lower() in blob)
            if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu"]):score-=20
            if any(z in (rec["license"] or "").lower() for z in ["cc0","cc by","public domain","no restrictions"]):score+=4
            if rec["url"] and rec["sha1"]:score+=2
            rec["score"]=score
            if score>1: records.append(rec)
        time.sleep(.15)
    records.sort(key=lambda x:(-x["score"],x["title"] or ""))
    allout[str(rid)]={"categories":catlog,"file_count":len(titles),"candidates":records[:30]}
    print("TARGET",rid,"CATS",catlog,"FILES",len(titles),"TOP",[(v["score"],v["title"],v["license"]) for v in records[:10]],flush=True)
(OUT/"species_category_candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
