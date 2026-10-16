import json,time,re,html
from pathlib import Path
import requests

OUT=Path("evidence/m5_t1_drugname_4_32"); OUT.mkdir(parents=True,exist_ok=True)
targets={
 4:{"taxon":"Bupleurum chinense","terms":["柴胡 中藥 Bupleurum root","柴胡 藥材","Bupleuri Radix","Bupleurum chinense dried root"],"role":["root","radix","dried","柴胡","藥材","药材"]},
 5:{"taxon":"Notopterygium incisum","terms":["羌活 中藥","羌活 藥材","Notopterygii Rhizoma et Radix","Notopterygium incisum dried rhizome root"],"role":["root","rhizome","dried","羌活","藥材","药材"]},
 6:{"taxon":"Saposhnikovia divaricata","terms":["防風 中藥","防风 药材","Saposhnikoviae Radix","Saposhnikovia divaricata dried root"],"role":["root","radix","dried","防風","防风","藥材","药材"]},
 8:{"taxon":"Cinnamomum cassia","terms":["桂枝 中藥","桂枝 藥材","Cinnamomi Ramulus","Cinnamomum cassia dried twig ramulus"],"role":["twig","ramulus","branch","桂枝","dried","藥材","药材"]},
 9:{"taxon":"Schizonepeta tenuifolia","terms":["荊芥 中藥","荆芥 药材","Schizonepetae Herba","Schizonepeta tenuifolia dried herb"],"role":["herb","aerial","dried","荊芥","荆芥","藥材","药材"]},
10:{"taxon":"Mentha canadensis","terms":["薄荷 中藥","薄荷 藥材","Menthae Haplocalycis Herba","Mentha canadensis dried herb"],"role":["herb","aerial","dried","薄荷","藥材","药材"]},
12:{"taxon":"Asarum sieboldii","terms":["細辛 中藥","细辛 药材","Asari Radix et Rhizoma","Asarum sieboldii dried root rhizome"],"role":["root","rhizome","dried","細辛","细辛","藥材","药材"]},
18:{"taxon":"Actaea cimicifuga","terms":["升麻 中藥","升麻 藥材","Cimicifugae Rhizoma","Actaea cimicifuga dried rhizome","Cimicifuga foetida dried rhizome"],"role":["rhizome","dried","升麻","藥材","药材"]},
23:{"taxon":"Vitex trifolia","terms":["蔓荊子 中藥","蔓荆子 药材","Viticis Fructus","Vitex trifolia dried fruit"],"role":["fruit","fructus","dried","蔓荊子","蔓荆子","藥材","药材"]},
24:{"taxon":"Spirodela polyrhiza","terms":["浮萍 中藥","浮萍 藥材","Spirodelae Herba","Spirodela polyrhiza dried herb"],"role":["herb","whole plant","dried","浮萍","藥材","药材"]},
27:{"taxon":"Ligusticum sinense","terms":["藁本 中藥","藁本 藥材","Ligustici Rhizoma et Radix","Ligusticum sinense dried rhizome root"],"role":["root","rhizome","dried","藁本","藥材","药材"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.5 medicinal-drug-name search"
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
out={}
for rid,t in targets.items():
    seen={}; qs=[]
    for term in t["terms"]:
        data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":40,
                  "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,
                  "format":"json","formatversion":2})
        pages=data.get("query",{}).get("pages",[]); qs.append({"term":term,"count":len(pages)})
        for p in pages:
            ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
            def e(k): return clean(em.get(k) or "")
            title=p.get("title") or ""
            seen[title]={"title":title,"url":ii.get("url"),"thumburl":ii.get("thumburl"),"sha1":ii.get("sha1"),
              "width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size"),
              "license":e("LicenseShortName"),"license_url":e("LicenseUrl"),"author":e("Artist"),
              "credit":e("Credit"),"description":e("ImageDescription"),"categories":e("Categories")}
        time.sleep(.55)
    def score(x):
        blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=0
        if t["taxon"].lower() in blob: sc+=12
        sc+=sum(4 for z in t["role"] if z.lower() in blob)
        if any(z in blob for z in ["chinese herbal medicine","herbal medicine","crude drug","materia medica","生薬","中藥","中药"]): sc+=8
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu","living plant","flower show"]): sc-=15
        lic=(x.get("license") or "").lower()
        if any(z in lic for z in ["cc0","cc by","public domain","no restrictions"]): sc+=5
        if x.get("url") and x.get("sha1"): sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    out[str(rid)]={"target":t,"queries":qs,"candidates":vals[:50]}
    print("TARGET",rid,t["taxon"],"UNIQUE",len(vals),"TOP",[(v["score"],v["title"],v["license"],v["description"][:100]) for v in vals[:12]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
