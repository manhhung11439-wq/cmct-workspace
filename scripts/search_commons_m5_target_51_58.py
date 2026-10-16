# rerun marker 2026-10-16T07:43+07 — manuscript roles re-locked; criteria unchanged
import json,time,re,html
from pathlib import Path
import requests

OUT=Path("evidence/m5_t1_target_51_58"); OUT.mkdir(parents=True,exist_ok=True)
targets={
 51:{"taxon":"Gentiana scabra","terms":["Gentiana scabra dried root","Gentianae Radix et Rhizoma","Longdan dried root","龙胆 中药","龍膽 藥材"],"role":["root","rhizome","radix","dried","龙胆","龍膽","藥材","药材"]},
 52:{"taxon":"Taraxacum mongolicum","terms":["Taraxacum mongolicum dried whole plant","Herba Taraxaci","蒲公英 中药","蒲公英 藥材"],"role":["whole plant","herba","dried","蒲公英","藥材","药材"]},
 53:{"taxon":"Isatis tinctoria","terms":["Isatis tinctoria dried root","Radix Isatidis","Banlangen dried root","板蓝根 中药","板藍根 藥材"],"role":["root","radix","dried","板蓝根","板藍根","藥材","药材"]},
 54:{"taxon":"Iris domestica","terms":["Iris domestica dried rhizome","Belamcanda chinensis dried rhizome","Rhizoma Belamcandae","Shegan dried rhizome","射干 中药","射干 藥材"],"role":["rhizome","dried","射干","藥材","药材"]},
 55:{"taxon":"Paeonia lactiflora","terms":["Paeonia lactiflora red peony root dried","Radix Paeoniae Rubra","Chishao dried root","赤芍 中药","赤芍 藥材"],"role":["root","radix","dried","赤芍","藥材","药材"]},
 56:{"taxon":"Lycium chinense","terms":["Lycium chinense dried root bark","Cortex Lycii","Digupi dried root bark","地骨皮 中药","地骨皮 藥材"],"role":["root bark","cortex","dried","地骨皮","藥材","药材"]},
 57:{"taxon":"Artemisia annua","terms":["Artemisia annua dried aerial herb","Herba Artemisiae Annuae","Qinghao dried herb","青蒿 中药","青蒿 藥材"],"role":["aerial","herba","dried","青蒿","藥材","药材"]},
 58:{"taxon":"Andrographis paniculata","terms":["Andrographis paniculata dried aerial herb","Herba Andrographitis","Chuanxinlian dried herb","穿心莲 中药","穿心蓮 藥材"],"role":["aerial","herba","dried","穿心莲","穿心蓮","藥材","药材"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.5 targeted crude-drug search"
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
