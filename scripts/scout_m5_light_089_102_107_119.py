import json, pathlib, requests, time, re, html
OUT=pathlib.Path("evidence/m5_light_screen_089_102_107_119"); OUT.mkdir(parents=True,exist_ok=True)
targets={
  89:"Excoecaria cochinchinensis",
  102:"Premna serratifolia",
  107:"Hibiscus rosa-sinensis",
  119:"Breynia fruticosa",
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/36.3 lightweight detached-part screen"
def get(url,params=None):
    last=None
    for i in range(6):
        r=s.get(url,params=params,timeout=90,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(30,2**i)); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get("value","")
    return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()
res={}
terms=["cut","harvest","detached","branch","twig","leaf","leaves","flower","specimen","hand"]
for rid,taxon in targets.items():
    pages={}
    for term in terms:
        q=f'"{taxon}" {term}'
        data=get("https://commons.wikimedia.org/w/api.php",{
          "action":"query","format":"json","generator":"search","gsrnamespace":6,
          "gsrsearch":q,"gsrlimit":20,
          "prop":"imageinfo","iiprop":"url|size|sha1|extmetadata"
        }).json()
        for p in data.get("query",{}).get("pages",{}).values():
            ii=p.get("imageinfo",[{}])[0]; m=ii.get("extmetadata",{})
            title=p.get("title",""); desc=clean(m.get("ImageDescription","")); cats=clean(m.get("Categories",""))
            blob=(title+" "+desc+" "+cats).lower()
            if taxon.lower() not in blob: continue
            lic=clean(m.get("LicenseShortName",""))
            if not any(k in lic.lower() for k in ["cc by","cc0","public domain"]): continue
            pages[p["pageid"]]={
              "title":title,"pageid":p["pageid"],"description":desc,"categories":cats,
              "author":clean(m.get("Artist","")),"credit":clean(m.get("Credit","")),
              "license_short":lic,"license_url":clean(m.get("LicenseUrl","")),
              "usage_terms":clean(m.get("UsageTerms","")),
              "original_url":ii.get("url"),"sha1":ii.get("sha1"),
              "width":ii.get("width"),"height":ii.get("height")
            }
    vals=list(pages.values())
    res[str(rid)]={"taxon":taxon,"candidates":vals}
    print("ROW",rid,"COUNT",len(vals),flush=True)
    for x in vals[:40]:
        print(json.dumps({"id":rid,**x},ensure_ascii=False),flush=True)
(OUT/"manifest.json").write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding="utf-8")
