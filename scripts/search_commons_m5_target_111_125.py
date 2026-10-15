import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_111_125"); OUT.mkdir(parents=True,exist_ok=True)
targets={
111:("Annona muricata",["Annona muricata harvested leaves","Annona muricata dried leaves","soursop leaves dried"],["leaf","leaves","fresh","dried","harvested"]),
112:("Pteris multifida",["Pteris multifida harvested whole plant","Pteris multifida dried herb","Pteridis multifidae herba"],["whole plant","herb","fresh","dried","harvested"]),
113:("Peristrophe bivalvis",["Peristrophe bivalvis harvested leaves stems","Peristrophe bivalvis dried herb","Peristrophe roxburghiana leaves"],["whole plant","leaves","stems","fresh","dried","harvested"]),
114:("Gynura procumbens",["Gynura procumbens fresh leaves stems harvested","Gynura procumbens edible leaves","Gynura procumbens market"],["leaf","leaves","young stems","fresh","harvested","edible"]),
117:("Commelina communis",["Commelina communis dried herb medicinal","Commelina communis harvested aerial herb","鸭跖草 中药"],["aerial","whole herb","dried","harvested","鸭跖草"]),
118:("Barleria lupulina",["Barleria lupulina harvested leaves twigs","Barleria lupulina fresh leaves medicinal","Barleria lupulina dried herb"],["leaf","leaves","twigs","fresh","dried","harvested"]),
120:("Ludwigia hyssopifolia",["Ludwigia hyssopifolia harvested aerial herb","Ludwigia hyssopifolia dried herb","rau muong medicinal"],["aerial","whole plant","fresh","dried","harvested"]),
122:("Paramignya trimera",["Paramignya trimera dried root stem slices","Paramignya trimera medicinal root","xao tam phan dried"],["root","stem","dried","sliced","medicinal"]),
123:("Scutellaria barbata",["Scutellaria barbata dried whole herb","Scutellariae Barbatae Herba","半枝莲 中药","半枝蓮 藥材"],["whole herb","herb","dried","半枝莲","半枝蓮","药材","藥材"]),
124:("Clinacanthus nutans",["Clinacanthus nutans fresh leaves young twigs harvested","Clinacanthus nutans leaves medicinal","Clinacanthus nutans dried leaves"],["leaf","leaves","twigs","fresh","dried","harvested"]),
125:("Scoparia dulcis",["Scoparia dulcis dried whole herb","Scoparia dulcis harvested whole plant","Cam thao dat dried herb"],["whole plant","herb","dried","harvested"]),
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/2.1 targeted T1 M5 111-125"
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
    if isinstance(v,dict):v=v.get("value") or ""
    v=html.unescape(str(v or ""));v=re.sub(r"<[^>]+>"," ",v);return " ".join(v.split())
for rid,(taxon,terms,roles) in targets.items():
    seen={}
    for term in terms:
        data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":30,
                  "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,
                  "format":"json","formatversion":2})
        for p in data.get("query",{}).get("pages",[]):
            ii=(p.get("imageinfo") or [{}])[0];em=ii.get("extmetadata") or {}
            def e(k):return clean(em.get(k) or "")
            title=p.get("title") or ""
            seen[title]={"title":title,"url":ii.get("url"),"thumburl":ii.get("thumburl"),"sha1":ii.get("sha1"),
                         "width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size"),
                         "license":e("LicenseShortName"),"license_url":e("LicenseUrl"),"author":e("Artist"),
                         "credit":e("Credit"),"description":e("ImageDescription"),"categories":e("Categories")}
        time.sleep(.45)
    def score(x):
        blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
        sc=(12 if taxon.lower() in blob else 0)+sum(4 for z in roles if z.lower() in blob)
        if any(z in blob for z in ["herbal medicine","medicinal","market","food","edible","crude drug"]):sc+=5
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu","growing plant","habitus"]):sc-=12
        if any(z in (x.get("license") or "").lower() for z in ["cc0","cc by","public domain","no restrictions"]):sc+=5
        if x.get("url") and x.get("sha1"):sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
    (OUT/f"{rid}.json").write_text(json.dumps(vals[:40],ensure_ascii=False,indent=2),encoding="utf-8")
