import json, pathlib, requests, time, html, re, hashlib, io, math
from PIL import Image, ImageOps, ImageDraw

OUT=pathlib.Path("evidence/m5_t1_fresh_detached_screen_059_089_102_114_115_124"); OUT.mkdir(parents=True,exist_ok=True)
TARGETS=[
 (59,"Callisia fragrans"),
 (89,"Excoecaria cochinchinensis"),
 (102,"Premna serratifolia"),
 (114,"Gynura procumbens"),
 (115,"Clerodendrum chinense"),
 (124,"Clinacanthus nutans"),
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/32.0 detached-harvested fresh material screen"
def get(u,params=None):
    last=None
    for i in range(7):
        r=s.get(u,params=params,timeout=120,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(45,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get("value","")
    return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()

allrows={}
for rid,species in TARGETS:
    cat="Category:"+species
    q=get("https://commons.wikimedia.org/w/api.php",{
      "action":"query","format":"json","generator":"categorymembers","gcmtitle":cat,
      "gcmtype":"file","gcmlimit":"50","prop":"imageinfo",
      "iiprop":"url|size|sha1|extmetadata","iiurlwidth":"600"
    }).json()
    rows=[]
    for p in (q.get("query",{}).get("pages",{}) or {}).values():
        ii=(p.get("imageinfo") or [{}])[0]; meta=ii.get("extmetadata",{})
        thumb=ii.get("thumburl") or ii.get("url")
        if not thumb: continue
        try:
            b=get(thumb).content; im=Image.open(io.BytesIO(b)); im.load(); im=ImageOps.exif_transpose(im).convert("RGB")
        except Exception:
            continue
        fn=OUT/f"{rid:03d}_{len(rows)+1:02d}.jpg"; im.save(fn,quality=86,optimize=True)
        row={"id":rid,"species":species,"title":p.get("title"),"pageid":p.get("pageid"),
             "thumburl":thumb,"original_url":ii.get("url"),"api_sha1":ii.get("sha1"),
             "width":ii.get("width"),"height":ii.get("height"),
             "description":clean(meta.get("ImageDescription","")),
             "author":clean(meta.get("Artist","")),"license_short":clean(meta.get("LicenseShortName","")),
             "license_url":clean(meta.get("LicenseUrl","")),"usage_terms":clean(meta.get("UsageTerms","")),
             "categories":clean(meta.get("Categories","")),"thumb_file":str(fn)}
        rows.append(row)
    allrows[str(rid)]=rows
    # contact sheet
    thumbs=[]
    for row in rows:
        im=Image.open(row["thumb_file"]).convert("RGB")
        im.thumbnail((240,180))
        card=Image.new("RGB",(260,230),"white"); card.paste(im,((260-im.width)//2,5))
        d=ImageDraw.Draw(card); d.text((5,188),row["title"][:38],fill="black"); d.text((5,205),f"{row['license_short']}",fill="black")
        thumbs.append(card)
    if thumbs:
        cols=4; rowsn=math.ceil(len(thumbs)/cols)
        sheet=Image.new("RGB",(cols*260,rowsn*230),"white")
        for i,card in enumerate(thumbs): sheet.paste(card,((i%cols)*260,(i//cols)*230))
        sheet.save(OUT/f"contact_{rid:03d}.jpg",quality=90)
    print("TARGET",rid,species,"FILES",len(rows),flush=True)
(OUT/"manifest.json").write_text(json.dumps(allrows,ensure_ascii=False,indent=2),encoding="utf-8")
