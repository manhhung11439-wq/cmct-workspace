import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_82_97"); OUT.mkdir(parents=True,exist_ok=True)
targets={
82:("Houttuynia cordata",["Houttuynia cordata harvested herb","Houttuynia cordata fresh bunch market","Houttuynia cordata dried herb","Herba Houttuyniae"],["herb","harvest","fresh","dried","bunch"]),
83:("Ageratum conyzoides",["Ageratum conyzoides harvested aerial parts","Ageratum conyzoides dried herb","Ageratum conyzoides medicinal herb"],["aerial","herb","harvest","dried","medicinal"]),
84:("Oroxylum indicum",["Oroxylum indicum dried bark","Oroxylum indicum dried seeds","Cortex Oroxyli","Semen Oroxyli"],["bark","seed","seeds","dried","cortex","semen"]),
85:("Euphorbia thymifolia",["Euphorbia thymifolia harvested whole plant","Euphorbia thymifolia dried herb","Euphorbia thymifolia medicinal herb"],["whole plant","herb","harvest","dried"]),
86:("Catharanthus roseus",["Catharanthus roseus dried whole plant root","Catharanthus roseus medicinal herb dried","Herba Catharanthi rosei"],["whole plant","root","dried","herb"]),
87:("Gymnanthemum amygdalinum",["Gymnanthemum amygdalinum fresh leaves","Vernonia amygdalina harvested leaves","Vernonia amygdalina dried leaves bitter leaf"],["leaf","leaves","fresh","harvest","dried"]),
88:("Jasminum subtriplinerve",["Jasminum subtriplinerve dried stems leaves","Jasminum subtriplinerve medicinal tea","chè vằng dried"],["stem","leaves","dried","tea","medicinal"]),
89:("Excoecaria cochinchinensis",["Excoecaria cochinchinensis dried leaves","Excoecaria cochinchinensis harvested leaves","Excoecaria cochinchinensis medicinal leaf"],["leaf","leaves","dried","harvest","medicinal"]),
92:("Eleusine indica",["Eleusine indica harvested whole plant roots","Eleusine indica dried whole herb","Eleusine indica medicinal herb"],["whole plant","root","roots","dried","herb"]),
93:("Bidens pilosa",["Bidens pilosa harvested aerial herb","Bidens pilosa dried herb","Bidens pilosa medicinal herb"],["aerial","herb","harvest","dried"]),
94:("Pulsatilla chinensis",["Pulsatilla chinensis dried root slices","Radix Pulsatillae","白頭翁 中药 根"],["root","radix","dried","白頭翁"]),
95:("Sophora tonkinensis",["Sophora tonkinensis dried root rhizome","Radix Sophorae Tonkinensis","山豆根 中药"],["root","rhizome","radix","dried","山豆根"]),
96:("Calvatia",["Calvatia gigantea mature dried fruitbody spores","Calvatia lilacina dried puffball spores","Lasiosphaera fenzlii dried puffball","马勃 中药"],["fruitbody","puffball","spore","spores","dried","马勃"]),
97:("Lobelia chinensis",["Lobelia chinensis dried whole herb","Herba Lobeliae Chinensis","半边莲 中药 全草"],["whole","herb","dried","半边莲"]),
}
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/1.7 target-82-97"
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
              "license":e("LicenseShortName"),"author":e("Artist"),"credit":e("Credit"),
              "description":e("ImageDescription"),"categories":e("Categories"),
              "width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size")}
        time.sleep(.4)
    def score(x):
        b=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=(10 if taxon.lower() in b else 0)+sum(4 for z in roles if z.lower() in b)
        if any(z in b for z in ("herbal medicine","chinese medicine","materia medica","medicinal","drug")):sc+=6
        if any(z in b for z in ("herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu")):sc-=14
        if any(z in (x.get("license") or "").lower() for z in ("cc0","cc by","public domain","no restrictions")):sc+=5
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"] or ""))
    for x in vals:x["score"]=score(x)
    allout[str(rid)]=vals[:40]
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:55]) for v in vals[:10]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
