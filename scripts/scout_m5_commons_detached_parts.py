import json, pathlib, time, requests, html, re, io, urllib.parse
from PIL import Image,ImageDraw
OUT=pathlib.Path("evidence/m5_commons_detached_screen"); OUT.mkdir(parents=True,exist_ok=True)
targets=[
 (30,"Citrus aurantiifolia","leaves leaf"),
 (31,"Vitex negundo","leaves leaf"),
 (60,"Pseuderanthemum palatiferum","leaves leaf"),
 (62,"Paederia lanuginosa","leaves leaf"),
 (89,"Excoecaria cochinchinensis","leaves leaf"),
 (102,"Premna serratifolia","leaves leaf"),
 (107,"Hibiscus rosa-sinensis","flower flowers"),
 (119,"Breynia fruticosa","leaves leaf"),
 (124,"Clinacanthus nutans","leaves leaf"),
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/35.1 Commons detached-part screen"
def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=180); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get("value","")
    return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()
def reusable(meta):
    lic=clean(meta.get("LicenseShortName","")).lower()
    return any(x in lic for x in ["cc by","cc0","public domain"]) and "nc" not in lic and "noncommercial" not in lic
manifest={}
for rid,sci,parts in targets:
    ro=OUT/f"{rid:03d}_{sci.replace(' ','_')}"; ro.mkdir(exist_ok=True)
    q=f'"{sci}" {parts}'
    data=get("https://commons.wikimedia.org/w/api.php",{
      "action":"query","format":"json","generator":"search","gsrnamespace":6,
      "gsrsearch":q,"gsrlimit":40,
      "prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","iiurlwidth":600
    }).json()
    pages=list((data.get("query") or {}).get("pages",{}).values())
    cands=[]; seq=0
    for p in pages:
        ii=(p.get("imageinfo") or [{}])[0]; meta=ii.get("extmetadata",{})
        if not reusable(meta): continue
        desc=clean(meta.get("ImageDescription","")); cats=clean(meta.get("Categories",""))
        hay=(p.get("title","")+" "+desc+" "+cats).lower()
        # exact scientific-name evidence must appear in title/description/categories.
        if sci.lower() not in hay and sci.replace(" ","_").lower() not in hay: continue
        thumb=ii.get("thumburl") or ii.get("url")
        try:
            b=get(thumb).content; im=Image.open(io.BytesIO(b)); im.load()
        except: continue
        seq+=1
        fp=ro/f"thumb_{seq:02d}.jpg"
        if (im.format or "").upper()!="JPEG":
            im.convert("RGB").save(fp,"JPEG",quality=88)
        else: fp.write_bytes(b)
        cands.append({
          "seq":seq,"title":p.get("title"),"pageid":p.get("pageid"),
          "description":desc,"categories":cats,
          "author":clean(meta.get("Artist","")),"credit":clean(meta.get("Credit","")),
          "license_short":clean(meta.get("LicenseShortName","")),
          "license_url":clean(meta.get("LicenseUrl","")),
          "usage_terms":clean(meta.get("UsageTerms","")),
          "original_url":ii.get("url"),"api_sha1":ii.get("sha1"),
          "width":ii.get("width"),"height":ii.get("height"),
          "thumb_file":str(fp)
        })
        if seq>=16: break
    # contact
    tiles=[]
    for c in cands:
        im=Image.open(c["thumb_file"]).convert("RGB"); im.thumbnail((230,170))
        tile=Image.new("RGB",(250,225),"white"); tile.paste(im,((250-im.width)//2,5))
        dr=ImageDraw.Draw(tile)
        label=f"{c['seq']:02d} {c['license_short']}\n{c['title'][:55]}"
        dr.multiline_text((5,180),label,fill="black",spacing=2)
        tiles.append(tile)
    if tiles:
        cols=4; rows=(len(tiles)+cols-1)//cols
        sheet=Image.new("RGB",(cols*250,rows*225+35),"white")
        ImageDraw.Draw(sheet).text((5,8),f"#{rid} {sci} — Commons reusable exact-name screen",fill="black")
        for i,t in enumerate(tiles): sheet.paste(t,((i%cols)*250,(i//cols)*225+35))
        sheet.save(ro/"contact.jpg",quality=90)
    manifest[str(rid)]={"science":sci,"query":q,"candidates":cands}
    print("TARGET",rid,sci,"candidates",len(cands),flush=True)
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
