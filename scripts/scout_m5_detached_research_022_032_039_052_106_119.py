import json, pathlib, time, requests, re, io
from PIL import Image,ImageOps,ImageDraw,ImageFont
OUT=pathlib.Path("evidence/m5_detached_research_screen_022_032_039_052_106_119"); OUT.mkdir(parents=True,exist_ok=True)
targets=[
 (22,"Centipeda minima"),
 (32,"Kyllinga nemoralis"),
 (39,"Scleromitrion diffusum"),
 (52,"Taraxacum mongolicum"),
 (106,"Glinus oppositifolius"),
 (119,"Breynia fruticosa"),
]
KW=re.compile(r"\b(specimen|collected|collect|uprooted|weeded|removed|harvested|harvest|plucked|picked|detached|cut\s+plant|voucher)\b",re.I)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/35.0 detached medicinal-material research scout"
def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=180); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def taxon_exact(name):
    data=get("https://api.inaturalist.org/v1/taxa",{"q":name,"per_page":30}).json()["results"]
    exact=[x for x in data if x.get("name","").lower()==name.lower() and x.get("rank")=="species"]
    return exact[0] if exact else None
manifest={}
for rid,name in targets:
    tx=taxon_exact(name)
    ro=OUT/f"{rid:03d}_{name.replace(' ','_')}"; ro.mkdir(exist_ok=True)
    rec={"target":{"id":rid,"name":name},"taxon":tx,"candidates":[]}
    if not tx:
        manifest[str(rid)]=rec; continue
    obs=get("https://api.inaturalist.org/v1/observations",{
        "taxon_id":tx["id"],"quality_grade":"research","photos":"true",
        "per_page":200,"order_by":"created_at","order":"desc"
    }).json()["results"]
    seq=0
    for o in obs:
        desc=o.get("description") or ""
        if not KW.search(desc): continue
        for ph in o.get("photos") or []:
            lic=(ph.get("license_code") or "").lower()
            if lic not in ("cc0","cc-by","cc-by-sa"): continue
            seq+=1
            url=(ph.get("url") or "").replace("square.","medium.")
            try:
                b=get(url).content; im=Image.open(io.BytesIO(b)); im.load()
            except: continue
            p=ro/f"thumb_{seq:02d}_{ph.get('id')}.jpg"; p.write_bytes(b)
            rec["candidates"].append({
                "seq":seq,"observation_id":o.get("id"),"photo_id":ph.get("id"),
                "license":lic,"taxon_id":o.get("taxon",{}).get("id"),
                "taxon_name":o.get("taxon",{}).get("name"),
                "quality_grade":o.get("quality_grade"),
                "observed_on":o.get("observed_on"),
                "place_guess":o.get("place_guess"),
                "description":desc,
                "photo_url":ph.get("url"),
                "thumb_url":url,"thumb_file":str(p),
                "attribution":ph.get("attribution")
            })
            if seq>=30: break
        if seq>=30: break
    # contact sheet
    thumbs=[]
    for c in rec["candidates"]:
        try:
            im=Image.open(c["thumb_file"]).convert("RGB")
            im.thumbnail((220,180))
            tile=Image.new("RGB",(250,230),"white")
            x=(250-im.width)//2; tile.paste(im,(x,5))
            dr=ImageDraw.Draw(tile)
            label=f"{c['seq']:02d} obs {c['observation_id']}\nphoto {c['photo_id']} {c['license']}\n{(c['description'] or '')[:65]}"
            dr.multiline_text((5,188),label,fill="black",spacing=2)
            thumbs.append(tile)
        except: pass
    if thumbs:
        cols=4; rows=(len(thumbs)+cols-1)//cols
        sheet=Image.new("RGB",(cols*250,rows*230+35),"white")
        ImageDraw.Draw(sheet).text((5,8),f"#{rid} {name} — keyword-detached research-grade reusable",fill="black")
        for i,t in enumerate(thumbs): sheet.paste(t,((i%cols)*250,(i//cols)*230+35))
        sheet.save(ro/"contact.jpg",quality=90)
    manifest[str(rid)]=rec
    print("TARGET",rid,name,"taxon",tx["id"],"candidates",len(rec["candidates"]),flush=True)
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
