import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_51_58"); OUT.mkdir(parents=True,exist_ok=True)
targets={
51:("Gentiana scabra",["Gentiana scabra dried root rhizome","Gentianae Radix et Rhizoma","Longdan dried root","龙胆 中药"],["root","rhizome","dried","龙胆"]),
52:("Taraxacum mongolicum",["Taraxacum mongolicum whole plant root","Taraxaci Herba dried","蒲公英 中药 全草","Taraxacum mongolicum harvested"],["whole plant","root","dried","蒲公英"]),
53:("Isatis tinctoria",["Isatis tinctoria dried root","Isatidis Radix","Banlangen dried root","板蓝根 中药"],["root","radix","dried","板蓝根"]),
54:("Iris domestica",["Iris domestica dried rhizome","Belamcanda chinensis dried rhizome","Rhizoma Belamcandae","射干 中药"],["rhizome","dried","射干"]),
55:("Paeonia lactiflora",["Paeonia lactiflora red peony root dried","Radix Paeoniae Rubra","赤芍 中药","Paeonia lactiflora dried root"],["root","radix","dried","赤芍"]),
56:("Lycium chinense",["Lycium chinense dried root bark","Cortex Lycii","Digupi root bark","地骨皮 中药"],["root bark","cortex","dried","地骨皮"]),
57:("Artemisia annua",["Artemisia annua dried herb","Herba Artemisiae Annuae","Qinghao dried herb","青蒿 中药"],["herb","aerial","dried","青蒿"]),
58:("Andrographis paniculata",["Andrographis paniculata dried herb","Herba Andrographitis","穿心莲 中药","Andrographis dried aerial parts"],["herb","aerial","dried","穿心莲"]),
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.5 targeted crude-drug search"
api="https://commons.wikimedia.org/w/api.php"
def get(params):
    last=None
    for i in range(8):
        r=s.get(api,params=params,timeout=90); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(int(r.headers.get("Retry-After") or min(45,2*(2**i)))); continue
        r.raise_for_status(); return r.json()
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get("value") or ""
    return " ".join(re.sub(r"<[^>]+>"," ",html.unescape(str(v or ""))).split())
for rid,(taxon,terms,roles) in targets.items():
    seen={}
    for term in terms:
        data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":25,
                  "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,"format":"json","formatversion":2})
        for p in data.get("query",{}).get("pages",[]):
            ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
            e=lambda k:clean(em.get(k) or "")
            seen[p.get("title") or ""]={"title":p.get("title"),"url":ii.get("url"),"sha1":ii.get("sha1"),
                "license":e("LicenseShortName"),"author":e("Artist"),"credit":e("Credit"),
                "description":e("ImageDescription"),"categories":e("Categories"),
                "width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size")}
        time.sleep(.45)
    def score(x):
        b=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=(12 if taxon.lower() in b else 0)+sum(4 for z in roles if z.lower() in b)
        if any(z in b for z in ("herbal medicine","chinese medicine","materia medica","medicinal")): sc+=6
        if any(z in b for z in ("herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu")): sc-=12
        if any(z in (x.get("license") or "").lower() for z in ("cc0","cc by","public domain","no restrictions")): sc+=5
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"] or ""))
    for x in vals:x["score"]=score(x)
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:50]) for v in vals[:10]],flush=True)
    (OUT/f"{rid}.json").write_text(json.dumps(vals[:40],ensure_ascii=False,indent=2),encoding="utf-8")
