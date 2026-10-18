import json, pathlib, time, requests, html, re, io
from PIL import Image, ImageDraw

OUT=pathlib.Path("evidence/m5_detached_broad_screen_060_062_067_068_107_113_114_116")
OUT.mkdir(parents=True,exist_ok=True)

targets=[
 (60,"Pseuderanthemum palatiferum",["leaf","leaves","plucked","picked","harvested","detached","specimen"]),
 (62,"Paederia lanuginosa",["leaf","leaves","plucked","picked","harvested","detached","food"]),
 (67,"Sphagneticola calendulacea",["whole plant","aerial","harvested","detached","specimen","weed"]),
 (68,"Phyllostachys nigra",["young leaves","leaf","leaves","harvested","detached"]),
 (107,"Hibiscus rosa-sinensis",["flower","flowers","plucked","picked","detached","hand"]),
 (113,"Peristrophe bivalvis",["leaf","leaves","whole plant","harvested","detached","specimen"]),
 (114,"Gynura procumbens",["leaf","leaves","stem","harvested","detached","food"]),
 (116,"Acanthus ilicifolius",["leaf","leaves","root","aerial","harvested","detached","specimen"]),
]

s=requests.Session()
s.headers["User-Agent"]="CMCT-image-audit/36.0 broad detached reusable material screen"

def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=180,allow_redirects=True)
        last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()

def clean(v):
    if isinstance(v,dict): v=v.get("value","")
    return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()

def reusable(meta):
    lic=(clean(meta.get("LicenseShortName",""))+" "+clean(meta.get("UsageTerms",""))).lower()
    if "noncommercial" in lic or "nc" in lic and "cc" in lic: return False
    return any(x in lic for x in ["cc by","cc0","public domain"])

manifest={}
for rid,sci,terms in targets:
    ro=OUT/f"{rid:03d}_{sci.replace(' ','_')}"
    ro.mkdir(exist_ok=True)
    seen={}
    for term in terms:
        q=f'"{sci}" {term}'
        data=get("https://commons.wikimedia.org/w/api.php",{
          "action":"query","format":"json","generator":"search","gsrnamespace":6,
          "gsrsearch":q,"gsrlimit":30,
          "prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","iiurlwidth":700
        }).json()
        for p in (data.get("query") or {}).get("pages",{}).values():
            ii=(p.get("imageinfo") or [{}])[0]; meta=ii.get("extmetadata",{})
            if not reusable(meta): continue
            desc=clean(meta.get("ImageDescription","")); cats=clean(meta.get("Categories",""))
            hay=(p.get("title","")+" "+desc+" "+cats).lower().replace("_"," ")
            if sci.lower() not in hay: continue
            key=p.get("pageid") or p.get("title")
            if key in seen: continue
            seen[key]={
              "title":p.get("title"),"pageid":p.get("pageid"),
              "description":desc,"categories":cats,
              "author":clean(meta.get("Artist","")),"credit":clean(meta.get("Credit","")),
              "license_short":clean(meta.get("LicenseShortName","")),
              "license_url":clean(meta.get("LicenseUrl","")),
              "usage_terms":clean(meta.get("UsageTerms","")),
              "original_url":ii.get("url"),"thumb_url":ii.get("thumburl") or ii.get("url"),
              "api_sha1":ii.get("sha1"),"width":ii.get("width"),"height":ii.get("height"),
              "matched_terms":[term],
            }
    cands=list(seen.values())[:24]
    # thumbnails
    tiles=[]
    kept=[]
    for idx,c in enumerate(cands,1):
        try:
            b=get(c["thumb_url"]).content
            im=Image.open(io.BytesIO(b)); im.load()
            fp=ro/f"thumb_{idx:02d}.jpg"
            if (im.format or "").upper()=="JPEG":
                fp.write_bytes(b)
            else:
                im.convert("RGB").save(fp,"JPEG",quality=90)
            c["seq"]=idx; c["thumb_file"]=str(fp); kept.append(c)
            im=Image.open(fp).convert("RGB"); im.thumbnail((230,170))
            tile=Image.new("RGB",(250,235),"white")
            tile.paste(im,((250-im.width)//2,5))
            dr=ImageDraw.Draw(tile)
            label=f"{idx:02d} {c['license_short']}\n{c['title'][:54]}"
            dr.multiline_text((5,180),label,fill="black",spacing=2)
            tiles.append(tile)
        except Exception:
            pass
    if tiles:
        cols=4; rows=(len(tiles)+cols-1)//cols
        sheet=Image.new("RGB",(cols*250,rows*235+40),"white")
        ImageDraw.Draw(sheet).text((5,8),f"#{rid} {sci} — reusable exact-taxon broad detached screen",fill="black")
        for i,t in enumerate(tiles):
            sheet.paste(t,((i%cols)*250,(i//cols)*235+40))
        sheet.save(ro/"contact.jpg",quality=90)
    manifest[str(rid)]={"science":sci,"candidates":kept}
    print("TARGET",rid,sci,"candidates",len(kept),flush=True)

(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
