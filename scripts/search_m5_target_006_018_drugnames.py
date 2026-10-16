import json,time,re,html
from pathlib import Path
import requests

OUT=Path("evidence/m5_t1_target_006_018_drugnames"); OUT.mkdir(parents=True,exist_ok=True)
targets={
 6:{"name":"Phòng Phong","taxon":"Saposhnikovia divaricata","terms":["防風 中藥","防风 中药","Saposhnikoviae Radix","Fangfeng Chinese medicine dried root","Saposhnikovia divaricata dried root"]},
 8:{"name":"Quế Chi","taxon":"Cinnamomum cassia","terms":["桂枝 中藥","桂枝 中药","Cinnamomi Ramulus","Guizhi Chinese medicine dried twig","Cinnamomum cassia dried twig"]},
 9:{"name":"Kinh Giới","taxon":"Schizonepeta tenuifolia","terms":["荊芥 中藥","荆芥 中药","Schizonepetae Herba","Jingjie dried herb","Schizonepeta tenuifolia dried herb"]},
 10:{"name":"Bạc Hà","taxon":"Mentha canadensis","terms":["薄荷 中藥 藥材","薄荷 中药 药材","Menthae Haplocalycis Herba","Bohe dried herb","Mentha canadensis dried herb"]},
 12:{"name":"Tế Tân","taxon":"Asarum sieboldii","terms":["細辛 中藥","细辛 中药","Asari Radix et Rhizoma","Xixin dried root rhizome","Asarum sieboldii dried root"]},
 15:{"name":"Tang Diệp","taxon":"Morus alba","terms":["桑葉 中藥","桑叶 中药","Mori Folium","Sangye dried leaf","Morus alba dried medicinal leaf"]},
 18:{"name":"Thăng Ma","taxon":"Actaea cimicifuga","terms":["升麻 中藥","升麻 中药","Cimicifugae Rhizoma","Shengma dried rhizome","Cimicifuga foetida dried rhizome"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/5.1 exact drug-name Commons search"
api="https://commons.wikimedia.org/w/api.php"
def get(params):
    last=None
    for i in range(8):
        r=s.get(api,params=params,timeout=90); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r.json()
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get("value") or ""
    v=html.unescape(str(v or "")); v=re.sub(r"<[^>]+>"," ",v)
    return " ".join(v.split())
allout={}
for rid,t in targets.items():
    seen={}; qlog=[]
    for term in t["terms"]:
        d=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":50,
               "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,
               "format":"json","formatversion":2})
        pages=d.get("query",{}).get("pages",[]); qlog.append({"term":term,"count":len(pages)})
        for p in pages:
            ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
            def e(k): return clean(em.get(k) or "")
            title=p.get("title") or ""
            seen[title]={"title":title,"url":ii.get("url"),"thumburl":ii.get("thumburl"),"sha1":ii.get("sha1"),
                         "w":ii.get("width"),"h":ii.get("height"),"bytes":ii.get("size"),
                         "license":e("LicenseShortName"),"license_url":e("LicenseUrl"),
                         "author":e("Artist"),"credit":e("Credit"),"description":e("ImageDescription"),
                         "categories":e("Categories")}
        time.sleep(.45)
    def score(x):
        b=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=0
        for z in [t["taxon"],"chinese medicine","herbal medicine","traditional chinese medicine","materia medica","dried","dry","radix","rhizoma","ramulus","herba","folium","藥材","药材","中藥","中药"]:
            if z.lower() in b: sc += 4 if z!=t["taxon"] else 10
        if any(z in b for z in ["herbarium","pressed specimen","living plant","flowering plant","botanical illustration","pdf","djvu"]): sc-=12
        lic=(x.get("license") or "").lower()
        if any(z in lic for z in ["cc0","cc by","public domain","no restrictions"]): sc+=5
        if x.get("url") and x.get("sha1"): sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    allout[str(rid)]={"target":t,"queries":qlog,"candidates":vals[:60]}
    print(rid,t["name"],"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:45]) for v in vals[:15]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
