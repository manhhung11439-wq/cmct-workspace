import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_76_90"); OUT.mkdir(parents=True,exist_ok=True)
targets={
76:("Patrinia scabiosifolia",["Patrinia scabiosifolia dried herb","Patriniae Herba","败酱草 中药","敗醬草 藥材"],["herb","whole plant","dried","败酱草","敗醬草","药材","藥材"]),
77:("Lithospermum erythrorhizon",["Lithospermum erythrorhizon dried root","Lithospermi Radix","紫草 中药","紫草 藥材"],["root","radix","dried","紫草","药材","藥材"]),
79:("Picrorhiza scrophulariiflora",["Picrorhiza scrophulariiflora dried rhizome","Picrorhizae Rhizoma","胡黄连 中药","胡黃連 藥材"],["rhizome","dried","胡黄连","胡黃連","药材","藥材"]),
80:("Cynanchum atratum",["Cynanchum atratum dried root rhizome","Cynanchi Atrati Radix et Rhizoma","白薇 中药","白薇 藥材"],["root","rhizome","dried","白薇","药材","藥材"]),
82:("Houttuynia cordata",["Houttuynia cordata fresh herb bunch","fish mint harvested","Houttuynia cordata dried herb","鱼腥草 中药"],["herb","aerial","fresh","dried","harvested","鱼腥草"]),
83:("Ageratum conyzoides",["Ageratum conyzoides harvested aerial herb","Ageratum conyzoides dried herb","fresh Ageratum herb"],["herb","aerial","fresh","dried","harvested"]),
84:("Oroxylum indicum",["Oroxylum indicum dried bark medicinal","Oroxylum indicum mature winged seeds","Oroxylum indicum crude drug"],["bark","seed","seeds","dried","medicinal"]),
85:("Euphorbia thymifolia",["Euphorbia thymifolia harvested whole plant","Euphorbia thymifolia dried herb","Euphorbia thymifolia fresh herb"],["whole plant","herb","fresh","dried","harvested"]),
86:("Catharanthus roseus",["Catharanthus roseus dried whole herb medicinal","Catharanthus roseus dried root medicinal","Catharanthus harvested medicinal"],["whole plant","root","dried","medicinal","harvested"]),
87:("Gymnanthemum amygdalinum",["Gymnanthemum amygdalinum fresh leaves harvested","Vernonia amygdalina leaves market","bitter leaf harvested"],["leaf","leaves","fresh","dried","harvested","bitter leaf"]),
88:("Jasminum subtriplinerve",["Jasminum subtriplinerve dried stems leaves","Che vang dried herb","Jasminum subtriplinerve medicinal"],["stems","leaves","dried","medicinal"]),
89:("Excoecaria cochinchinensis",["Excoecaria cochinchinensis harvested leaves twigs","Excoecaria cochinchinensis dried leaves","Don la do medicinal"],["leaves","twigs","fresh","dried","harvested"]),
90:("Sauropus androgynus",["Sauropus androgynus fresh leaves bunch","katuk leaves market","Sauropus androgynus dried root"],["leaf","leaves","fresh","root","dried","harvested"]),
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.8 targeted T1 M5 76-90"
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
        if any(z in blob for z in ["herbal medicine","medicinal","market","food","crude drug"]):sc+=5
        if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut",".pdf",".djvu","growing plant","habitus"]):sc-=12
        if any(z in (x.get("license") or "").lower() for z in ["cc0","cc by","public domain","no restrictions"]):sc+=5
        if x.get("url") and x.get("sha1"):sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
    for x in vals:x["score"]=score(x)
    print(rid,taxon,"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:12]],flush=True)
    (OUT/f"{rid}.json").write_text(json.dumps(vals[:40],ensure_ascii=False,indent=2),encoding="utf-8")
