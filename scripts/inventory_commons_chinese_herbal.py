# rerun marker 2026-10-16T09:20+07 — post-REV17 unresolved crude-drug inventory
import json,time,re,html,collections
from pathlib import Path
import requests

OUT=Path("evidence/commons_chinese_herbal_inventory"); OUT.mkdir(parents=True,exist_ok=True)
api="https://commons.wikimedia.org/w/api.php"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/2.0 Chinese-herbal category inventory"

targets={
4:["Bupleurum chinense","Bupleuri","柴胡"],
5:["Notopterygium incisum","Notopterygii","羌活"],
6:["Saposhnikovia divaricata","Saposhnikoviae","防风","防風"],
8:["Cinnamomum cassia","Cinnamomi Ramulus","桂枝"],
9:["Schizonepeta tenuifolia","Schizonepetae","荆芥","荊芥"],
10:["Mentha canadensis","Menthae Herba","薄荷"],
12:["Asarum sieboldii","Asari Radix","细辛","細辛"],
14:["Magnolia biondii","Magnoliae Flos","辛夷"],
15:["Morus alba","Mori Folium","桑叶","桑葉"],
18:["Cimicifuga foetida","Actaea cimicifuga","Cimicifugae Rhizoma","升麻"],
21:["Elsholtzia ciliata","Elsholtziae Herba","香薷"],
22:["Centipeda minima","Centipedae Herba","鹅不食草","鵝不食草"],
23:["Vitex trifolia","Viticis Fructus","蔓荆子","蔓荊子"],
24:["Spirodela polyrhiza","Spirodelae Herba","浮萍"],
27:["Ligusticum sinense","Ligustici Rhizoma","藁本","稿本"],
30:["Citrus aurantiifolia","lime leaves","柠檬叶","檸檬葉"],
33:["Paeonia suffruticosa","Moutan Cortex","牡丹皮"],
40:["Senna tora","Cassiae Semen","决明子","決明子"],
43:["Scutellaria baicalensis","Scutellariae Radix","黄芩","黃芩"],
44:["Coptis chinensis","Coptidis Rhizoma","黄连","黃連"],
45:["Phellodendron chinense","Phellodendri Chinensis Cortex","川黄柏","川黃柏"],
47:["Forsythia suspensa","Forsythiae Fructus","连翘","連翹"],
48:["Gardenia jasminoides","Gardeniae Fructus","栀子","梔子"],
51:["Gentiana scabra","Gentianae Radix","龙胆","龍膽"],
53:["Isatis tinctoria","Isatidis Radix","板蓝根","板藍根"],
54:["Iris domestica","Belamcanda chinensis","Belamcandae Rhizoma","射干"],
55:["Paeonia lactiflora","Paeoniae Rubra","赤芍"],
56:["Lycium chinense","Lycii Cortex","地骨皮"],
57:["Artemisia annua","Artemisiae Annuae Herba","青蒿"],
58:["Andrographis paniculata","Andrographidis Herba","穿心莲","穿心蓮"],
70:["Sophora flavescens","Sophorae Flavescentis Radix","苦参","苦參"],
71:["Dictamnus dasycarpus","Dictamni Cortex","白鲜皮","白鮮皮"],
72:["Fraxinus rhynchophylla","Fraxini Cortex","秦皮"],
74:["Isatis tinctoria","Isatidis Folium","大青叶","大青葉"],
75:["Strobilanthes cusia","Indigo Naturalis","青黛"],
77:["Lithospermum erythrorhizon","Arnebia","Lithospermi Radix","紫草"],
79:["Picrorhiza scrophulariiflora","Picrorhizae Rhizoma","胡黄连","胡黃連"],
80:["Cynanchum atratum","Cynanchi Atrati Radix","白薇"],
91:["Nelumbo nucifera","Nelumbinis Folium","荷叶","荷葉"],
94:["Pulsatilla chinensis","Pulsatillae Radix","白头翁","白頭翁"],
95:["Sophora tonkinensis","Sophorae Tonkinensis Radix","山豆根"],
97:["Lobelia chinensis","Lobeliae Chinensis Herba","半边莲","半邊蓮"],
101:["Paris polyphylla","Paridis Rhizoma","重楼","重樓"],
123:["Scutellaria barbata","Scutellariae Barbatae Herba","半枝莲","半枝蓮"],
}

def get(params):
    last=None
    for i in range(8):
        r=s.get(api,params=params,timeout=90); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(int(r.headers.get("Retry-After") or min(60,2*(2**i)))); continue
        r.raise_for_status(); return r.json()
    last.raise_for_status()

def clean(v):
    if isinstance(v,dict):v=v.get("value") or ""
    return " ".join(re.sub(r"<[^>]+>"," ",html.unescape(str(v or ""))).split())

roots=["Chinese herbal medicines","Traditional Chinese medicine","Kampo"]
q=collections.deque((r,0) for r in roots)
seen_cats=set(); files=set()
MAX_DEPTH=2
while q:
    cat,depth=q.popleft()
    if cat in seen_cats or depth>MAX_DEPTH:continue
    seen_cats.add(cat)
    cont=None
    while True:
        p={"action":"query","list":"categorymembers","cmtitle":"Category:"+cat,
           "cmtype":"file|subcat","cmlimit":"500","format":"json","formatversion":2}
        if cont:p["cmcontinue"]=cont
        d=get(p)
        for m in d.get("query",{}).get("categorymembers",[]):
            title=m.get("title") or ""
            if title.startswith("File:"):files.add(title)
            elif title.startswith("Category:") and depth<MAX_DEPTH:q.append((title[9:],depth+1))
        cont=(d.get("continue") or {}).get("cmcontinue")
        if not cont:break
    print("CAT",cat,"depth",depth,"files_so_far",len(files),"queue",len(q),flush=True)
    if len(seen_cats)>300:break

records=[]
flist=sorted(files)
for i in range(0,len(flist),50):
    d=get({"action":"query","titles":"|".join(flist[i:i+50]),"prop":"imageinfo",
           "iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2})
    for p in d.get("query",{}).get("pages",[]):
        ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}; e=lambda k:clean(em.get(k) or "")
        rec={"title":p.get("title"),"url":ii.get("url"),"sha1":ii.get("sha1"),"size":ii.get("size"),
             "width":ii.get("width"),"height":ii.get("height"),"license":e("LicenseShortName"),
             "license_url":e("LicenseUrl"),"author":e("Artist"),"credit":e("Credit"),
             "description":e("ImageDescription"),"categories":e("Categories")}
        records.append(rec)
    time.sleep(.25)

matches={}
for rid,terms in targets.items():
    vals=[]
    for rec in records:
        blob=" ".join(str(rec.get(k) or "") for k in ("title","description","categories")).lower()
        matched=[t for t in terms if t.lower() in blob]
        if matched:
            lic=(rec.get("license") or "").lower()
            sc=10*len(matched)
            if any(x in blob for x in ["dried","crude drug","herbal medicine","chinese medicine","生药","生藥","药材","藥材"]):sc+=5
            if any(x in blob for x in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu"]):sc-=10
            if any(x in lic for x in ["cc0","cc by","public domain","no restrictions"]):sc+=4
            vals.append({"score":sc,"matched":matched,**rec})
    vals.sort(key=lambda x:(-x["score"],x["title"] or ""))
    matches[str(rid)]=vals[:40]
    print("TARGET",rid,"N",len(vals),"TOP",[(v["score"],v["title"],v["license"],v["matched"]) for v in vals[:10]],flush=True)

(OUT/"inventory_summary.json").write_text(json.dumps({
 "categories_scanned":sorted(seen_cats),"file_count":len(files),"matches":matches
},ensure_ascii=False,indent=2),encoding="utf-8")
