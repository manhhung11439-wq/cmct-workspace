# resume marker 2026-10-16T15:12+07 — revisit missing early M5 from promoted REV17
import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_04_15"); OUT.mkdir(parents=True,exist_ok=True)
targets={
4:("Bupleurum chinense",["Bupleurum chinense dried root","Bupleuri Radix","柴胡 中药","柴胡 藥材"],["root","radix","dried","柴胡","药材","藥材"]),
5:("Notopterygium incisum",["Notopterygium incisum dried root rhizome","Notopterygii Rhizoma et Radix","羌活 中药","羌活 藥材"],["root","rhizome","dried","羌活","药材","藥材"]),
6:("Saposhnikovia divaricata",["Saposhnikovia divaricata dried root","Saposhnikoviae Radix","防风 中药","防風 藥材"],["root","radix","dried","防风","防風","药材","藥材"]),
7:("Ephedra sinica",["Ephedra sinica dried stems","Ephedrae Herba","麻黄 中药","麻黃 藥材"],["stem","stems","herb","dried","麻黄","麻黃","药材","藥材"]),
8:("Cinnamomum cassia",["Cinnamomum cassia dried twig","Cinnamomi Ramulus","桂枝 中药","桂枝 藥材"],["twig","ramulus","dried","桂枝","药材","藥材"]),
9:("Schizonepeta tenuifolia",["Schizonepeta tenuifolia dried herb","Schizonepetae Herba","荆芥 中药","荊芥 藥材"],["herb","aerial","dried","荆芥","荊芥","药材","藥材"]),
10:("Mentha canadensis",["Mentha canadensis dried herb","Menthae Haplocalycis Herba","薄荷 中药","薄荷 藥材"],["herb","aerial","dried","薄荷","药材","藥材"]),
12:("Asarum sieboldii",["Asarum sieboldii dried root rhizome","Asari Radix et Rhizoma","细辛 中药","細辛 藥材"],["root","rhizome","dried","细辛","細辛","药材","藥材"]),
14:("Magnolia biondii",["Magnolia biondii dried flower buds","Magnoliae Flos","辛夷 中药","辛夷 藥材"],["flower bud","buds","flos","dried","辛夷","药材","藥材"]),
15:("Morus alba",["Morus alba dried leaves medicinal","Mori Folium","桑叶 中药","桑葉 藥材"],["leaf","leaves","folium","dried","桑叶","桑葉","药材","藥材"]),
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/2.2 targeted T1 M5 04-15"
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
        if any(z in blob for z in ["herbal medicine","chinese medicine","medicinal","crude drug"]):sc+=6
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu","growing plant","habitus"]):sc-=12
        if any(z in (x.get("license") or "").lower() for z in ["cc0","cc by","public domain","no restrictions"]):sc+=5
        if x.get("url") and x.get("sha1"):sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
    (OUT/f"{rid}.json").write_text(json.dumps(vals[:40],ensure_ascii=False,indent=2),encoding="utf-8")
