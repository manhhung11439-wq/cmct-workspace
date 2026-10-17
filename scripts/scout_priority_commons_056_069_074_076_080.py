import json,hashlib,pathlib,time,requests,html,re
from PIL import Image
OUT=pathlib.Path("evidence/m5_priority_commons_056_069_074_076_080"); OUT.mkdir(parents=True,exist_ok=True)
targets=[
 {"id":56,"queries":["Lycii Cortex","Cortex Lycii","Lycium chinense root bark","Digupi"]},
 {"id":69,"queries":["Lophatheri Herba","Danzhuye","Lophatherum gracile dried","淡竹葉 藥材"]},
 {"id":74,"queries":["Isatidis Folium","Da Qing Ye","Isatis tinctoria dried leaves","大青葉 藥材"]},
 {"id":76,"queries":["Patriniae Herba","Patrinia scabiosifolia dried","Bai Jiang Cao","败酱草 药材"]},
 {"id":80,"queries":["Cynanchi Atrati Radix","Cynanchum atratum dried root","Bai Wei root","白薇 药材"]},
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/24.1 priority Commons drug-material scout"
def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get("value","")
    return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
allrows=[]
for tar in targets:
    seen=set(); rows=[]
    tdir=OUT/f"{tar['id']:03d}"; tdir.mkdir(exist_ok=True)
    for q in tar["queries"]:
        js=get("https://commons.wikimedia.org/w/api.php",{
          "action":"query","format":"json","list":"search","srnamespace":6,"srlimit":12,
          "srsearch":q
        }).json()
        for hit in js.get("query",{}).get("search",[]):
            title=hit["title"]
            if title in seen: continue
            seen.add(title)
            try:
                iq=get("https://commons.wikimedia.org/w/api.php",{
                  "action":"query","format":"json","prop":"imageinfo","titles":title,
                  "iiprop":"url|size|sha1|extmetadata"
                }).json()
                p=next(iter(iq["query"]["pages"].values()))
                ii=(p.get("imageinfo") or [None])[0]
                if not ii: continue
                meta=ii.get("extmetadata",{})
                row={"id":tar["id"],"query":q,"title":title,"pageid":p.get("pageid"),
                  "description":clean(meta.get("ImageDescription","")),"author":clean(meta.get("Artist","")),
                  "license_short":clean(meta.get("LicenseShortName","")),"license_url":clean(meta.get("LicenseUrl","")),
                  "usage_terms":clean(meta.get("UsageTerms","")),"categories":clean(meta.get("Categories","")),
                  "original_url":ii.get("url"),"api_sha1":ii.get("sha1"),"api_width":ii.get("width"),"api_height":ii.get("height")}
                blobtxt=(title+" "+row["description"]+" "+row["categories"]).lower()
                material_kw=any(k in blobtxt for k in ["dried","dry ","herba","cortex","radix","root bark","药材","藥材","饮片","飲片","herb","medicine","medicinal","market","shop"])
                if material_kw and ii.get("url"):
                    b=get(ii["url"]).content
                    ext=pathlib.Path(ii["url"].split("?")[0]).suffix.lower()
                    if ext not in [".jpg",".jpeg",".png",".webp"]: ext=".jpg"
                    fn=tdir/f"cand_{len(rows)+1:02d}{ext}"; fn.write_bytes(b)
                    try:
                        im=Image.open(fn); im.load()
                        s1,s256=hh(b)
                        row.update({"file":str(fn),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"local_sha1":s1,"local_sha256":s256,"hash_match":s1==ii.get("sha1")})
                    except Exception:
                        fn.unlink(missing_ok=True)
                rows.append(row); print("ROW="+json.dumps(row,ensure_ascii=False),flush=True)
    (tdir/"manifest.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    allrows.extend(rows)
(OUT/"batch_manifest.json").write_text(json.dumps(allrows,ensure_ascii=False,indent=2),encoding="utf-8")
