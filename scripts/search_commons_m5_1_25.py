# resume marker 2026-10-16T15:12+07 — strict early-slot recheck from promoted REV17
import json, time, re
from pathlib import Path
import requests

OUT=Path("evidence/m5_t1_1_25_commons")
OUT.mkdir(parents=True,exist_ok=True)
rows={
1:["Puerariae Lobatae Radix","kudzu root dried slices","葛根 中药"],
2:["Perillae Folium dried","Perilla frutescens dried leaf","紫苏叶 中药"],
4:["Bupleuri Radix","Bupleurum chinense dried root","柴胡 中药"],
5:["Notopterygii Rhizoma et Radix","Notopterygium incisum dried root","羌活 中药"],
6:["Saposhnikoviae Radix","Saposhnikovia divaricata dried root","防风 中药"],
7:["Ephedrae Herba","Ephedra sinica dried stem","麻黄 中药"],
8:["Cinnamomi Ramulus","Cinnamomum cassia twig dried","桂枝 中药"],
9:["Schizonepetae Herba","Schizonepeta tenuifolia dried","荆芥 中药"],
10:["Menthae Herba","Mentha canadensis dried herb","薄荷 中药"],
11:["Angelicae Dahuricae Radix","Angelica dahurica dried root","白芷 中药"],
12:["Asari Radix et Rhizoma","Asarum sieboldii dried root","细辛 中药"],
13:["Xanthii Fructus","Xanthium strumarium dried fruit","苍耳子 中药"],
14:["Magnoliae Flos","Magnolia biondii dried flower bud","辛夷 中药"],
15:["Mori Folium","Morus alba dried leaf","桑叶 中药"],
16:["Chrysanthemi Flos","Chrysanthemum morifolium dried flower","菊花 中药"],
17:["Arctii Fructus","Arctium lappa dried fruit seed","牛蒡子 中药"],
18:["Cimicifugae Rhizoma","Cimicifuga foetida dried rhizome","升麻 中药"],
19:["Cryptotympana atrata exuvia dried","cicada slough Chinese medicine","蝉蜕 中药"],
20:["Cymbopogon citratus dried herb","lemongrass dried medicinal","香茅 药材"],
21:["Elsholtziae Herba","Elsholtzia ciliata dried herb","香薷 中药"],
22:["Centipedae Herba","Centipeda minima dried herb","鹅不食草 中药"],
23:["Viticis Fructus","Vitex trifolia dried fruit","蔓荆子 中药"],
24:["Spirodelae Herba","Spirodela polyrhiza dried","浮萍 中药"],
25:["Sojae Semen Praeparatum","Dan Dou Chi medicinal fermented soybean","淡豆豉 中药"],
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.0 (systematic medicinal-material audit)"
api="https://commons.wikimedia.org/w/api.php"
allout={}
for rid,terms in rows.items():
    seen={}
    qlog=[]
    for term in terms:
        params={
          "action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":12,
          "prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","iiurlwidth":800,
          "format":"json","formatversion":2
        }
        for attempt in range(8):
            r=s.get(api,params=params,timeout=60)
            if r.status_code==429:
                wait=int(r.headers.get("Retry-After") or (5*(attempt+1)))
                print("RATE_LIMIT", rid, term, "wait", wait, flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            data=r.json()
            break
        else:
            print("SKIP_RATE_LIMIT", rid, term, flush=True)
            continue
        qlog.append({"term":term,"count":len(data.get("query",{}).get("pages",[]))})
        for p in data.get("query",{}).get("pages",[]):
            ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
            def val(k):
                v=em.get(k) or {}
                return v.get("value") if isinstance(v,dict) else v
            title=p.get("title")
            seen[title]={
              "title":title,
              "pageid":p.get("pageid"),
              "url":ii.get("url"),
              "thumburl":ii.get("thumburl"),
              "width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size"),"sha1":ii.get("sha1"),
              "license":val("LicenseShortName"),"license_url":val("LicenseUrl"),"artist":val("Artist"),
              "credit":val("Credit"),"description":val("ImageDescription"),"object_name":val("ObjectName"),
              "categories":val("Categories"),
            }
        time.sleep(1.5)
    vals=list(seen.values())
    # rough relevance score: medicinal terms + permissive license
    def score(x):
        blob=" ".join(str(x.get(k) or "") for k in ["title","description","object_name","categories"]).lower()
        sc=0
        if any(z in blob for z in ["radix","rhizoma","herba","folium","flos","fructus","semen","中药","medicine","medicinal","dried"]): sc+=3
        lic=(x.get("license") or "").lower()
        if lic.startswith("cc by") or lic=="cc0" or "public domain" in lic: sc+=2
        if x.get("url"): sc+=1
        return sc
    vals.sort(key=lambda x:(-score(x),x.get("title") or ""))
    allout[str(rid)]={"queries":qlog,"candidates":vals[:30]}
    print(rid, qlog, "unique",len(vals), "top",[(v["title"],v["license"]) for v in vals[:5]])
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
