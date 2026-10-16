# resume marker 2026-10-16T15:12+07 — revisit missing 30-40 from promoted REV17
import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_30_40"); OUT.mkdir(parents=True,exist_ok=True)
targets={
30:("Citrus aurantiifolia",["Citrus aurantiifolia harvested leaves","lime leaves fresh","Citrus aurantiifolia dried leaves"],["leaf","leaves","fresh","dried","harvested"]),
31:("Vitex negundo",["Vitex negundo harvested leaves","Vitex negundo dried leaves medicinal","Viticis Negundo Folium"],["leaf","leaves","fresh","dried","harvested"]),
32:("Kyllinga nemoralis",["Kyllinga nemoralis harvested whole herb","Kyllinga nemoralis dried herb medicinal"],["whole herb","whole plant","fresh","dried","harvested"]),
33:("Paeonia suffruticosa",["Paeonia suffruticosa dried root bark","Moutan Cortex","牡丹皮 中药","牡丹皮 藥材"],["root bark","cortex","dried","牡丹皮","药材","藥材"]),
34:("Solanum procumbens",["Solanum procumbens dried whole herb","Solanum procumbens medicinal herb","cà gai leo dried herb"],["whole herb","whole plant","dried","medicinal"]),
35:("Cynara scolymus",["Cynara scolymus dried leaves medicinal","artichoke dried leaves tea","Cynara leaf dried"],["leaf","leaves","dried","medicinal"]),
36:("Phyllanthus urinaria",["Phyllanthus urinaria dried whole herb","Phyllanthi Urinariae Herba","珍珠草 中药"],["whole herb","whole plant","dried","珍珠草"]),
37:("Gymnema sylvestre",["Gymnema sylvestre dried leaves medicinal","Gymnema leaves dried","Gurmar dried leaves"],["leaf","leaves","dried","medicinal"]),
38:("Celastrus hindsii",["Celastrus hindsii dried stems leaves","Celastrus hindsii medicinal herb","xạ đen dried"],["stems","leaves","dried","medicinal"]),
39:("Hedyotis diffusa",["Hedyotis diffusa dried whole herb","Scleromitrion diffusum dried herb","白花蛇舌草 中药","白花蛇舌草 藥材"],["whole herb","dried","白花蛇舌草","药材","藥材"]),
40:("Senna tora",["Senna tora dried mature seeds","Cassiae Semen","决明子 中药","決明子 藥材"],["seed","seeds","semen","dried","决明子","決明子","药材","藥材"]),
}
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/2.4 targeted T1 M5 30-40"
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
        if any(z in blob for z in ["herbal medicine","chinese medicine","medicinal","crude drug","tea"]):sc+=6
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu","growing plant","habitus"]):sc-=12
        if any(z in (x.get("license") or "").lower() for z in ["cc0","cc by","public domain","no restrictions"]):sc+=5
        if x.get("url") and x.get("sha1"):sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
    (OUT/f"{rid}.json").write_text(json.dumps(vals[:40],ensure_ascii=False,indent=2),encoding="utf-8")
