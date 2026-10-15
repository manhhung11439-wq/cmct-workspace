import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_59_75"); OUT.mkdir(parents=True,exist_ok=True)
targets={
59:("Callisia fragrans",["Callisia fragrans harvested leaves stems","Callisia fragrans fresh leaves","Callisia fragrans dried herb"],["leaf","leaves","stem","harvest","dried"]),
60:("Pseuderanthemum palatiferum",["Pseuderanthemum palatiferum fresh leaves","Pseuderanthemum palatiferum picked leaves","Pseuderanthemum palatiferum dried leaves"],["leaf","leaves","fresh","dried"]),
61:("Helicteres hirsuta",["Helicteres hirsuta dried stems leaves","Helicteres hirsuta medicinal herb","An xoa dried herb"],["stem","branch","leaves","dried","medicinal"]),
62:("Paederia lanuginosa",["Paederia lanuginosa fresh leaves","Paederia lanuginosa picked leaves","Paederia lanuginosa leaf"],["leaf","leaves","fresh","picked"]),
63:("Ampelopsis cantoniensis",["Ampelopsis cantoniensis dried stems leaves","Ampelopsis cantoniensis medicinal tea","chè dây dried herb"],["stem","leaves","dried","tea","medicinal"]),
64:("Hedyotis capitellata",["Hedyotis capitellata dried stems leaves","Hedyotis capitellata medicinal herb","dạ cẩm dried herb"],["stem","leaves","dried","medicinal"]),
65:("Crinum latifolium",["Crinum latifolium dried leaves","Crinum latifolium sliced leaves","Crinum latifolium medicinal leaves"],["leaf","leaves","dried","sliced","medicinal"]),
67:("Sphagneticola calendulacea",["Sphagneticola calendulacea harvested whole plant","Wedelia chinensis fresh herb","Sphagneticola calendulacea dried herb"],["herb","whole plant","harvest","fresh","dried"]),
68:("Phyllostachys nigra",["Phyllostachys nigra young leaves harvested","Phyllostachys nigra dried leaves","竹葉 中药 竹叶"],["leaf","leaves","young","dried","竹葉","竹叶"]),
69:("Lophatherum gracile",["Lophatherum gracile dried herb","Herba Lophatheri","淡竹葉 中药"],["herb","dried","lophatheri","淡竹葉"]),
70:("Sophora flavescens",["Sophora flavescens dried root slices","Radix Sophorae Flavescentis","苦參 中药 根"],["root","radix","dried","苦參"]),
71:("Dictamnus dasycarpus",["Dictamnus dasycarpus dried root bark","Cortex Dictamni","白鮮皮 中药"],["root bark","cortex","dried","白鮮皮"]),
72:("Fraxinus rhynchophylla",["Fraxinus rhynchophylla dried bark","Cortex Fraxini","秦皮 中药"],["bark","cortex","dried","秦皮"]),
73:("Viola yedoensis",["Viola yedoensis harvested whole plant","Viola yedoensis dried herb","紫花地丁 中药"],["whole plant","herb","fresh","dried","紫花地丁"]),
74:("Isatis tinctoria",["Isatis tinctoria dried leaves","Folium Isatidis","大青葉 中药"],["leaf","leaves","dried","大青葉"]),
75:("Strobilanthes cusia",["Indigo Naturalis Strobilanthes cusia","青黛 中药 粉","natural indigo medicinal powder"],["indigo","powder","青黛","medicinal"]),
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.6 target-59-75"
api="https://commons.wikimedia.org/w/api.php"
def get(params):
    last=None
    for i in range(8):
        r=s.get(api,params=params,timeout=90);last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(int(r.headers.get("Retry-After") or min(45,2*(2**i))));continue
        r.raise_for_status();return r.json()
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict):v=v.get("value") or ""
    return " ".join(re.sub(r"<[^>]+>"," ",html.unescape(str(v or ""))).split())
allout={}
for rid,(taxon,terms,roles) in targets.items():
    seen={}
    for term in terms:
        data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":25,
                  "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,"format":"json","formatversion":2})
        for p in data.get("query",{}).get("pages",[]):
            ii=(p.get("imageinfo") or [{}])[0];em=ii.get("extmetadata") or {};e=lambda k:clean(em.get(k) or "")
            seen[p.get("title") or ""]={"title":p.get("title"),"url":ii.get("url"),"sha1":ii.get("sha1"),
             "license":e("LicenseShortName"),"author":e("Artist"),"credit":e("Credit"),"description":e("ImageDescription"),
             "categories":e("Categories"),"width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size")}
        time.sleep(.4)
    def score(x):
        b=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=(12 if taxon.lower() in b else 0)+sum(4 for z in roles if z.lower() in b)
        if any(z in b for z in ("herbal medicine","chinese medicine","materia medica","medicinal","herb","drug")):sc+=5
        if any(z in b for z in ("herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu")):sc-=14
        if any(z in (x.get("license") or "").lower() for z in ("cc0","cc by","public domain","no restrictions")):sc+=5
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"] or ""))
    for x in vals:x["score"]=score(x)
    allout[str(rid)]=vals[:40]
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:55]) for v in vals[:10]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
