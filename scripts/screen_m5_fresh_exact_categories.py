import json,pathlib,time,requests,html,re,io,hashlib
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_fresh_exact_category_screen"); OUT.mkdir(parents=True,exist_ok=True)
targets=[
 (59,"Callisia fragrans","Cây Lược Vàng"),
 (60,"Pseuderanthemum palatiferum","Cây Hoàn Ngọc"),
 (62,"Paederia lanuginosa","Lá Mơ Lông"),
 (89,"Excoecaria cochinchinensis","Đơn Lá Đỏ"),
 (102,"Premna serratifolia","Vọng Cách"),
 (114,"Gynura procumbens","Bầu Đất"),
 (115,"Clerodendrum chinense","Bạch Đồng Nữ"),
 (119,"Breynia fruticosa","Bồ Cu Vẽ"),
 (124,"Clinacanthus nutans","Xương Khỉ"),
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/32.1 exact-category harvested-material screen"
def get(u,params=None):
  last=None
  for i in range(8):
    r=s.get(u,params=params,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(30,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
def clean(v):
  if isinstance(v,dict): v=v.get("value","")
  return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()
for rid,species,vn in targets:
  tdir=OUT/f"m5_{rid:03d}"; tdir.mkdir(exist_ok=True)
  # exact Commons category members
  cm=get("https://commons.wikimedia.org/w/api.php",{
    "action":"query","format":"json","list":"categorymembers","cmtitle":"Category:"+species,
    "cmnamespace":6,"cmtype":"file","cmlimit":30
  }).json().get("query",{}).get("categorymembers",[])
  rows=[]
  for idx,item in enumerate(cm,1):
    title=item["title"]
    q=get("https://commons.wikimedia.org/w/api.php",{
      "action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|sha1|extmetadata",
      "iiurlwidth":480,"titles":title
    }).json()
    p=next(iter(q.get("query",{}).get("pages",{}).values()))
    ii=(p.get("imageinfo") or [{}])[0]; meta=ii.get("extmetadata",{})
    thumb=ii.get("thumburl") or ii.get("url")
    if not thumb: continue
    try:
      b=get(thumb).content; im=Image.open(io.BytesIO(b)).convert("RGB"); im.load()
    except Exception: continue
    fn=tdir/f"thumb_{idx:03d}.jpg"; im.save(fn,quality=88)
    row={"idx":idx,"id":rid,"target":vn,"species":species,"title":title,
      "description":clean(meta.get("ImageDescription","")),"author":clean(meta.get("Artist","")),
      "license_short":clean(meta.get("LicenseShortName","")),"license_url":clean(meta.get("LicenseUrl","")),
      "usage_terms":clean(meta.get("UsageTerms","")),"copyrighted":clean(meta.get("Copyrighted","")),
      "categories":clean(meta.get("Categories","")),"original_url":ii.get("url"),"api_sha1":ii.get("sha1"),
      "original_width":ii.get("width"),"original_height":ii.get("height"),"thumb_file":str(fn)}
    rows.append(row)
  (tdir/"manifest.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
  # contact sheets 12 each
  for si in range(0,len(rows),12):
    subset=rows[si:si+12]; tiles=[]
    for row in subset:
      im=Image.open(row["thumb_file"]).convert("RGB"); im.thumbnail((300,210))
      tile=Image.new("RGB",(320,280),"white"); tile.paste(im,((320-im.width)//2,5))
      d=ImageDraw.Draw(tile)
      lab=f"{row['idx']}. {row['title'][5:42]}\n{row['license_short']}"
      d.text((6,220),lab,fill="black")
      tiles.append(tile)
    if tiles:
      cols=3; rn=(len(tiles)+cols-1)//cols
      sh=Image.new("RGB",(cols*320,rn*280),"white")
      for i,t in enumerate(tiles): sh.paste(t,((i%cols)*320,(i//cols)*280))
      sh.save(tdir/f"contact_{si//12+1:02d}.jpg",quality=88)
  print("TARGET",rid,species,"FILES",len(rows),flush=True)
