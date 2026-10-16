# resume marker 2026-10-16T15:12+07 — gap-fill omitted rows 106,107,115,116,119,121
import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_101_125"); OUT.mkdir(parents=True,exist_ok=True)
T={
101:("Paris polyphylla",["Paris polyphylla dried rhizome","Paridis Rhizoma dried","重楼 中药 根茎"],["rhizome","dried","重楼"]),
102:("Premna serratifolia",["Premna serratifolia harvested leaves","Premna serratifolia fresh leaves market","Premna serratifolia dried leaves"],["leaf","leaves","fresh","harvest","dried"]),
103:("Tiliacora triandra",["Tiliacora triandra fresh harvested leaves","Tiliacora triandra leaves market","yanang leaves harvested"],["leaf","leaves","fresh","harvest","market"]),
104:("Platostoma palustre",["Platostoma palustre dried aerial herb","Mesona chinensis dried herb","grass jelly herb dried"],["aerial","herb","dried","grass jelly"]),
105:("Peperomia pellucida",["Peperomia pellucida harvested whole plant","Peperomia pellucida fresh whole herb","Peperomia pellucida bunch"],["whole plant","herb","fresh","harvest","bunch"]),
106:("Glinus oppositifolius",["Glinus oppositifolius harvested whole plant","Glinus oppositifolius dried herb","Glinus oppositifolius medicinal herb"],["whole plant","herb","fresh","dried","harvest"]),
107:("Hibiscus rosa-sinensis",["Hibiscus rosa-sinensis harvested flower","Hibiscus rosa-sinensis fresh flowers","Hibiscus rosa-sinensis leaves harvested"],["flower","flowers","leaf","leaves","harvest"]),
108:("Blumea lacera",["Blumea lacera harvested aerial herb","Blumea lacera dried herb","Blumea lacera medicinal herb"],["aerial","herb","fresh","dried","harvest"]),
109:("Terminalia catappa",["Terminalia catappa harvested leaves","Terminalia catappa dried leaves","Indian almond leaves dried"],["leaf","leaves","harvest","dried"]),
110:("Mangifera indica",["Mangifera indica harvested leaves","mango leaves bunch","dried mango leaves"],["leaf","leaves","harvest","bunch","dried"]),
111:("Annona muricata",["Annona muricata harvested leaves","soursop leaves dried","soursop leaves bunch"],["leaf","leaves","harvest","dried","bunch"]),
112:("Pteris multifida",["Pteris multifida harvested whole plant","Pteris multifida dried herb","Pteris multifida medicinal herb"],["whole plant","herb","dried","harvest"]),
113:("Peristrophe bivalvis",["Peristrophe bivalvis harvested leaves stems","Peristrophe bivalvis fresh leaves","Peristrophe bivalvis dried herb"],["leaf","leaves","stem","fresh","dried","harvest"]),
114:("Gynura procumbens",["Gynura procumbens harvested leaves young stems","Gynura procumbens fresh leaves","Gynura procumbens leaves market"],["leaf","leaves","young stems","fresh","harvest","market"]),
115:("Clerodendrum chinense",["Clerodendrum chinense harvested leaves","Clerodendrum chinense dried root","Clerodendrum chinense flowers harvested"],["leaf","leaves","root","flower","harvest","dried"]),
116:("Acanthus ilicifolius",["Acanthus ilicifolius dried root","Acanthus ilicifolius medicinal root","Acanthus ilicifolius harvested root"],["root","dried","harvest","medicinal"]),
117:("Commelina communis",["Commelina communis dried aerial herb","Commelina communis harvested whole herb","鸭跖草 中药"],["aerial","whole","herb","dried","鸭跖草"]),
118:("Barleria lupulina",["Barleria lupulina harvested leaves young twigs","Barleria lupulina fresh leaves","Barleria lupulina medicinal leaves"],["leaf","leaves","young twigs","fresh","harvest"]),
119:("Breynia fruticosa",["Breynia fruticosa harvested leaves twigs","Breynia fruticosa dried root","Breynia fruticosa medicinal herb"],["leaf","leaves","twigs","root","dried","harvest"]),
120:("Ludwigia hyssopifolia",["Ludwigia hyssopifolia harvested aerial plant","Ludwigia hyssopifolia dried herb","Ludwigia hyssopifolia medicinal herb"],["aerial","whole plant","herb","dried","harvest"]),
121:("Phyllanthus acidus",["Phyllanthus acidus harvested leaves","Phyllanthus acidus fresh fruit harvested","star gooseberry leaves dried"],["leaf","leaves","fruit","fresh","harvest","dried"]),
122:("Paramignya trimera",["Paramignya trimera dried root stem slices","Paramignya trimera medicinal root","xao tam phan dried root"],["root","stem","sliced","dried","medicinal"]),
123:("Scutellaria barbata",["Scutellaria barbata dried whole herb flowering","Herba Scutellariae Barbatae","半枝莲 中药"],["whole","herb","flowering","dried","半枝莲"]),
124:("Clinacanthus nutans",["Clinacanthus nutans harvested leaves young twigs","Clinacanthus nutans fresh leaves","Clinacanthus nutans dried leaves"],["leaf","leaves","young twigs","fresh","dried","harvest"]),
125:("Scoparia dulcis",["Scoparia dulcis dried whole herb","Scoparia dulcis harvested whole plant","Scoparia dulcis medicinal herb"],["whole","herb","dried","harvest","medicinal"]),
}
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/1.8 target-101-125"
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
for rid,(taxon,terms,roles) in T.items():
    seen={}
    for term in terms:
        data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":25,
                  "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,"format":"json","formatversion":2})
        for p in data.get("query",{}).get("pages",[]):
            ii=(p.get("imageinfo") or [{}])[0];em=ii.get("extmetadata") or {};e=lambda k:clean(em.get(k) or "")
            seen[p.get("title") or ""]={"title":p.get("title"),"url":ii.get("url"),"sha1":ii.get("sha1"),
             "license":e("LicenseShortName"),"author":e("Artist"),"credit":e("Credit"),"description":e("ImageDescription"),
             "categories":e("Categories"),"width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size")}
        time.sleep(.35)
    def score(x):
        b=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=(10 if taxon.lower() in b else 0)+sum(4 for z in roles if z.lower() in b)
        if any(z in b for z in ("herbal medicine","chinese medicine","materia medica","medicinal","drug","market","food")):sc+=5
        if any(z in b for z in ("herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu")):sc-=14
        if any(z in (x.get("license") or "").lower() for z in ("cc0","cc by","public domain","no restrictions")):sc+=5
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"] or ""))
    for x in vals:x["score"]=score(x)
    allout[str(rid)]=vals[:50]
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:55]) for v in vals[:10]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
