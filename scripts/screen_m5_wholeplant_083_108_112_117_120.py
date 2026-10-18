import json, pathlib, time, requests, hashlib, io, math
from PIL import Image, ImageOps, ImageDraw, ImageFont
OUT=pathlib.Path("evidence/m5_fresh_wholeplant_screen_083_108_112_117_120"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/34.1 exact harvested-whole-plant iNaturalist screen"
targets=[
 {"id":83,"name":"Ageratum conyzoides"},
 {"id":108,"name":"Blumea lacera"},
 {"id":112,"name":"Pteris multifida"},
 {"id":117,"name":"Commelina communis"},
 {"id":120,"name":"Ludwigia hyssopifolia"},
]
ok_licenses={"cc0","cc-by","cc-by-sa"}
def get(url,params=None):
    last=None
    for i in range(8):
        r=s.get(url,params=params,timeout=120); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(40,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()

def exact_taxon(name):
    data=get("https://api.inaturalist.org/v1/taxa",{"q":name,"rank":"species","per_page":30}).json()["results"]
    for x in data:
        if x.get("name")==name:
            return {"id":x["id"],"name":x["name"],"preferred_common_name":x.get("preferred_common_name"),"is_active":x.get("is_active")}
    raise RuntimeError("Exact taxon not found: "+name)

def thumb_url(photo):
    u=photo.get("url") or ""
    # iNat URLs usually square; medium preserves enough for visual screen
    return u.replace("square.","medium.") if "square." in u else u

def draw_sheet(rows,outfile,title):
    W,H=300,260; cols=4
    n=min(len(rows),48); rows=rows[:n]
    sh=math.ceil(n/cols); canvas=Image.new("RGB",(cols*W,sh*H+45),"white")
    d=ImageDraw.Draw(canvas); d.text((10,10),title,fill="black")
    for i,r in enumerate(rows):
        x=(i%cols)*W; y=(i//cols)*H+45
        try:
            im=Image.open(r["thumb_file"]).convert("RGB")
            im.thumbnail((W-12,H-58))
            px=x+(W-im.width)//2; py=y+4
            canvas.paste(im,(px,py))
        except: pass
        label=f'{r["seq"]:02d} obs {r["observation_id"]} / photo {r["photo_id"]}\n{r["license"] or "no-license"}'
        d.multiline_text((x+6,y+H-48),label,fill="black",spacing=2)
    canvas.save(outfile,quality=88)

manifest={}
for t in targets:
    tx=exact_taxon(t["name"]); td=OUT/f'{t["id"]:03d}_{t["name"].replace(" ","_")}'; td.mkdir(exist_ok=True)
    selected=[]; seen=set()
    # high-yield description searches first, then generic research-grade.
    queries=["uprooted","pulled","collected","specimen","harvested",None]
    for q in queries:
        params={"taxon_id":tx["id"],"quality_grade":"research","photos":"true","per_page":100,"order_by":"created_at","order":"desc"}
        if q: params["q"]=q
        try: obs=get("https://api.inaturalist.org/v1/observations",params).json()["results"]
        except Exception: continue
        for o in obs:
            oid=o["id"]
            for p in o.get("photos") or []:
                lic=(p.get("license_code") or "").lower()
                if lic not in ok_licenses: continue
                pid=p["id"]
                if pid in seen: continue
                seen.add(pid)
                u=thumb_url(p)
                try:
                    b=get(u).content; im=Image.open(io.BytesIO(b)); im.load()
                except Exception: continue
                seq=len(selected)+1; fn=td/f'thumb_{seq:02d}_{pid}.jpg'
                if im.mode!="RGB": im=im.convert("RGB")
                im.save(fn,format="JPEG",quality=88)
                selected.append({
                  "seq":seq,"observation_id":oid,"photo_id":pid,"license":lic,
                  "taxon_id":tx["id"],"taxon_name":tx["name"],
                  "obs_quality_grade":o.get("quality_grade"),"observed_on":o.get("observed_on"),
                  "place_guess":o.get("place_guess"),"description":o.get("description"),
                  "photo_url":p.get("url"),"thumb_url":u,"thumb_file":str(fn),
                  "attribution":p.get("attribution")
                })
                if len(selected)>=48: break
            if len(selected)>=48: break
        if len(selected)>=48: break
    draw_sheet(selected,td/"contact.jpg",f'#{t["id"]} {t["name"]} — exact iNaturalist research-grade, reusable photos')
    manifest[str(t["id"])]={"target":t,"taxon":tx,"candidates":selected}
    print("TARGET",t["id"],t["name"],"taxon",tx["id"],"candidates",len(selected),flush=True)
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
