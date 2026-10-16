# resume marker 2026-10-16T15:12+07 — continue target 76-85 from promoted REV17
import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_76_85"); OUT.mkdir(parents=True,exist_ok=True)
targets={
76:{"taxon":"Patrinia scabiosifolia","terms":["Patrinia scabiosifolia dried whole herb","Patriniae Herba","Bai Jiang Cao dried herb","敗醬草 中藥","败酱草 药材"],"role":["whole herb","herba","dried","敗醬草","败酱草","藥材","药材"]},
77:{"taxon":"Lithospermum erythrorhizon","terms":["Lithospermum erythrorhizon dried root slices","Lithospermi Radix","Zicao dried root","紫草 中藥","紫草 藥材"],"role":["root","radix","dried","slice","紫草","藥材","药材"]},
79:{"taxon":"Picrorhiza scrophulariiflora","terms":["Picrorhiza scrophulariiflora dried rhizome","Picrorhizae Rhizoma","Huhuanglian dried rhizome","胡黃連 中藥","胡黄连 药材"],"role":["rhizome","dried","胡黃連","胡黄连","藥材","药材"]},
80:{"taxon":"Cynanchum atratum","terms":["Cynanchum atratum dried root rhizome","Cynanchi Atrati Radix","Baiwei dried root","白薇 中藥","白薇 藥材"],"role":["root","rhizome","radix","dried","白薇","藥材","药材"]},
82:{"taxon":"Houttuynia cordata","terms":["Houttuynia cordata harvested fresh herb","Houttuynia cordata dried herb","Houttuyniae Herba","魚腥草 中藥","鱼腥草 药材"],"role":["herb","aerial","fresh","dried","魚腥草","鱼腥草","藥材","药材"]},
83:{"taxon":"Ageratum conyzoides","terms":["Ageratum conyzoides harvested aerial herb","Ageratum conyzoides dried herb","Herba Agerati","ageratum medicinal herb"],"role":["aerial","herb","fresh","dried","medicinal"]},
84:{"taxon":"Oroxylum indicum","terms":["Oroxylum indicum dried bark","Cortex Oroxyli","Oroxylum indicum dried seed","Semen Oroxyli","木蝴蝶 中藥","木蝴蝶 藥材"],"role":["bark","cortex","seed","semen","dried","木蝴蝶","藥材","药材"]},
85:{"taxon":"Euphorbia thymifolia","terms":["Euphorbia thymifolia harvested whole plant","Euphorbia thymifolia dried herb","Herba Euphorbiae thymifoliae","cỏ sữa dried herb"],"role":["whole plant","herb","fresh","dried","medicinal"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.8 targeted M5 76-85"
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
        time.sleep(.45)
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
