import io,json,hashlib,pathlib,time,requests,html,re,math
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_092_eleusine_series"); OUT.mkdir(parents=True,exist_ok=True)
TITLES=[
 "File:Goosegrass (18653350940).jpg",
 "File:Goosegrass (18843734841).jpg",
 "File:Goosegrass (18653297008).jpg",
 "File:Goosegrass (18841033445).jpg",
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/23.1 Eleusine indica Cornell series"
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
rows=[]; ims=[]
for i,title in enumerate(TITLES,1):
 q=get("https://commons.wikimedia.org/w/api.php",params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","titles":title}).json()
 p=next(iter(q["query"]["pages"].values())); ii=p["imageinfo"][0]; m=ii.get("extmetadata",{})
 b=get(ii["url"]).content; fn=OUT/f"candidate_{i:02d}.jpg"; fn.write_bytes(b)
 im=Image.open(fn); im.seek(0); im=im.convert("RGB"); s1,s256=hh(b); assert s1==ii.get("sha1")
 row={"title":title,"pageid":p.get("pageid"),"original_url":ii["url"],"api_sha1":ii.get("sha1"),"sha1":s1,"sha256":s256,"bytes":len(b),
      "width":im.width,"height":im.height,"file":str(fn),"description":clean(m.get("ImageDescription","")),"author":clean(m.get("Artist","")),
      "license":clean(m.get("LicenseShortName","")),"license_url":clean(m.get("LicenseUrl","")),"categories":clean(m.get("Categories",""))}
 rows.append(row); ims.append((im,row))
 print("CANDIDATE="+json.dumps(row,ensure_ascii=False),flush=True)
cellw,cellh=760,610; sheet=Image.new("RGB",(cellw*2,cellh*2),"white"); dr=ImageDraw.Draw(sheet)
for k,(im,row) in enumerate(ims):
 x=(k%2)*cellw; y=(k//2)*cellh; th=ImageOps.contain(im,(720,480)); sheet.paste(th,(x+20,y+20))
 dr.text((x+20,y+510),f"{k+1}: {row['title']}",fill="black"); dr.text((x+20,y+540),row['description'][:105],fill="black")
sheet.save(OUT/"contact.jpg",quality=90)
(OUT/"manifest.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
