import json, pathlib, requests, time, re, html
from PIL import Image,ImageOps,ImageDraw
from io import BytesIO

OUT=pathlib.Path("evidence/m5_fresh_whole_083_112_117_120"); OUT.mkdir(parents=True,exist_ok=True)
targets={
  83:("Ageratum conyzoides","Ageratum conyzoides"),
  112:("Pteris multifida","Pteris multifida"),
  117:("Commelina communis","Commelina communis"),
  120:("Ludwigia hyssopifolia","Ludwigia hyssopifolia"),
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/36.0 exact detached whole-plant scout"

def get(url,params=None):
    last=None
    for i in range(7):
        r=s.get(url,params=params,timeout=120,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(30,2**i)); continue
        r.raise_for_status(); return r
    last.raise_for_status()

def clean(v):
    if isinstance(v,dict): v=v.get("value","")
    return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()

def reusable(meta):
    lic=clean(meta.get("LicenseShortName","")).lower()
    return any(x in lic for x in ["cc by","cc0","public domain"])

manifest={}
for rid,(taxon,query) in targets.items():
    rd=OUT/f"{rid:03d}_{taxon.replace(' ','_')}"; rd.mkdir(exist_ok=True)
    # Commons file search weighted toward detached/whole-plant wording.
    qs=[
      f'"{query}" uprooted',
      f'"{query}" "whole plant"',
      f'"{query}" specimen',
      f'"{query}" root',
      f'"{query}" plant'
    ]
    pages={}
    for q in qs:
        data=get("https://commons.wikimedia.org/w/api.php",{
          "action":"query","format":"json","generator":"search","gsrnamespace":6,
          "gsrsearch":q,"gsrlimit":30,
          "prop":"imageinfo","iiprop":"url|size|sha1|extmetadata"
        }).json()
        for p in data.get("query",{}).get("pages",{}).values():
            if "imageinfo" not in p: continue
            ii=p["imageinfo"][0]; meta=ii.get("extmetadata",{})
            if not reusable(meta): continue
            title=p.get("title","")
            desc=clean(meta.get("ImageDescription",""))
            cats=clean(meta.get("Categories",""))
            # exact identity gate in title/description/categories
            blob=(title+" "+desc+" "+cats).lower()
            if query.lower() not in blob: continue
            pages[p["pageid"]]={
              "title":title,"pageid":p["pageid"],"description":desc,"categories":cats,
              "author":clean(meta.get("Artist","")),"credit":clean(meta.get("Credit","")),
              "license_short":clean(meta.get("LicenseShortName","")),
              "license_url":clean(meta.get("LicenseUrl","")),
              "usage_terms":clean(meta.get("UsageTerms","")),
              "original_url":ii.get("url"),"thumb_url":ii.get("thumburl") or ii.get("url"),
              "api_sha1":ii.get("sha1"),"width":ii.get("width"),"height":ii.get("height")
            }
    cand=list(pages.values())[:24]
    thumbs=[]
    for i,c in enumerate(cand,1):
        try:
            rr=get(c["thumb_url"]); im=Image.open(BytesIO(rr.content)); im.load()
            im.thumbnail((360,260))
            tf=rd/f"thumb_{i:02d}.jpg"; im.convert("RGB").save(tf,quality=86)
            c["seq"]=i;c["thumb_file"]=str(tf); thumbs.append((tf,c["title"]))
        except Exception as e:
            c["thumb_error"]=repr(e)
    # contact
    if thumbs:
        w,h=760,340
        rows=(len(thumbs)+3)//4
        sheet=Image.new("RGB",(w*4,h*rows),"white"); d=ImageDraw.Draw(sheet)
        for i,(tf,title) in enumerate(thumbs):
            im=Image.open(tf).convert("RGB")
            x=(i%4)*w; y=(i//4)*h
            sheet.paste(im,(x+(w-im.width)//2,y+20))
            d.text((x+10,y+290),f"{i+1:02d} {title[:95]}",fill="black")
        sheet.save(rd/"contact.jpg",quality=90)
    manifest[str(rid)]={"science":taxon,"candidates":cand}
    print("ROW",rid,"CANDIDATES",len(cand),flush=True)
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
