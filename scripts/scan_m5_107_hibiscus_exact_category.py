import json,hashlib,pathlib,time,requests,html,re,io
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_107_hibiscus_exact_category"); OUT.mkdir(parents=True,exist_ok=True)
CAT="Category:Hibiscus rosa-sinensis (flowers)"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/31.4 exact Hibiscus rosa-sinensis flower category screen"
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
members=[]; cont=None
while True:
    p={"action":"query","format":"json","list":"categorymembers","cmtitle":CAT,"cmnamespace":6,"cmlimit":"max"}
    if cont: p["cmcontinue"]=cont
    q=get("https://commons.wikimedia.org/w/api.php",p).json()
    members.extend(q["query"]["categorymembers"])
    cont=q.get("continue",{}).get("cmcontinue")
    if not cont: break
rows=[]
for i,m in enumerate(members,1):
    title=m["title"]
    q=get("https://commons.wikimedia.org/w/api.php",{
      "action":"query","format":"json","prop":"imageinfo",
      "iiprop":"url|size|sha1|extmetadata","iiurlwidth":520,"titles":title
    }).json()
    p=next(iter(q["query"]["pages"].values()))
    if "imageinfo" not in p: continue
    ii=p["imageinfo"][0]; meta=ii.get("extmetadata",{})
    thumb=ii.get("thumburl") or ii.get("url")
    try:
        b=get(thumb).content; im=Image.open(io.BytesIO(b)); im.load()
    except Exception: continue
    ext=".jpg" if im.format=="JPEG" else ".png"
    fp=OUT/f"thumb_{len(rows)+1:03d}{ext}"; fp.write_bytes(b)
    rows.append({"idx":len(rows)+1,"title":title,"pageid":p.get("pageid"),"original_url":ii.get("url"),
      "api_sha1":ii.get("sha1"),"orig_width":ii.get("width"),"orig_height":ii.get("height"),
      "thumb_file":str(fp),"description":clean(meta.get("ImageDescription","")),
      "author":clean(meta.get("Artist","")),"license_short":clean(meta.get("LicenseShortName","")),
      "license_url":clean(meta.get("LicenseUrl","")),"categories":clean(meta.get("Categories",""))})
(OUT/"manifest.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
# Contact sheets, 12 tiles per page.
for start in range(0,len(rows),12):
    group=rows[start:start+12]; cols=3; tw,th=420,330
    sh=Image.new("RGB",(cols*tw,((len(group)+cols-1)//cols)*th),"white")
    for j,row in enumerate(group):
        im=ImageOps.exif_transpose(Image.open(row["thumb_file"])).convert("RGB"); im.thumbnail((400,240))
        tile=Image.new("RGB",(tw,th),"white"); tile.paste(im,((tw-im.width)//2,4))
        d=ImageDraw.Draw(tile)
        label=f"{row['idx']}. {row['title'][:42]}\n{row['license_short']}"
        d.text((8,250),label,fill="black")
        sh.paste(tile,((j%cols)*tw,(j//cols)*th))
    sh.save(OUT/f"contact_{start//12+1:02d}.jpg",quality=90)
print("TOTAL="+str(len(rows)),flush=True)
print("MANIFEST="+json.dumps(rows,ensure_ascii=False),flush=True)

# rerun 2026-10-17 Batch32 exact-category refresh
