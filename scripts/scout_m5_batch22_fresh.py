import io,json,hashlib,pathlib,time,re,html,math
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
OUT=pathlib.Path("evidence/m5_t1_fresh_scout_batch22"); OUT.mkdir(parents=True,exist_ok=True)
targets=[
 {"id":22,"name":"Centipeda minima","terms":["uprooted","whole plant","plant","herb"]},
 {"id":32,"name":"Kyllinga nemoralis","terms":["uprooted","whole plant","plant","root"]},
 {"id":59,"name":"Callisia fragrans","terms":["cut leaves","leaves","shoot","plant"]},
 {"id":60,"name":"Pseuderanthemum palatiferum","terms":["leaves","harvested","plant"]},
 {"id":67,"name":"Sphagneticola calendulacea","terms":["whole plant","uprooted","plant"]},
 {"id":83,"name":"Ageratum conyzoides","terms":["uprooted","whole plant","medicinal","plant"]},
 {"id":85,"name":"Euphorbia thymifolia","terms":["uprooted","whole plant","plant"]},
 {"id":92,"name":"Eleusine indica","terms":["uprooted","whole plant","root","plant"]},
 {"id":93,"name":"Bidens pilosa","terms":["uprooted","whole plant","harvested","plant"]},
 {"id":107,"name":"Hibiscus rosa-sinensis","terms":["picked flower","fallen flower","flower in hand","flower"]},
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/22.0 controlled harvested-material scout"
API="https://commons.wikimedia.org/w/api.php"
def get(params):
  last=None
  for i in range(8):
    r=s.get(API,params=params,timeout=180); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(60,2*(2**i))); continue
    r.raise_for_status(); return r.json()
  last.raise_for_status()
def clean(v):
  if isinstance(v,dict): v=v.get("value","")
  return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()
def sha256(b): return hashlib.sha256(b).hexdigest()
allrows={}
for tar in targets:
  pool={}
  queries=[tar["name"]]+[f'{tar["name"]} {x}' for x in tar["terms"]]
  for q in queries:
    data=get({"action":"query","format":"json","generator":"search","gsrnamespace":6,"gsrlimit":20,"gsrsearch":q,
              "prop":"imageinfo","iiprop":"url|size|sha1|extmetadata"})
    for p in data.get("query",{}).get("pages",{}).values():
      ii=(p.get("imageinfo") or [{}])[0]; m=ii.get("extmetadata",{})
      title=p.get("title",""); desc=clean(m.get("ImageDescription","")); cats=clean(m.get("Categories",""))
      hay=(title+" "+desc+" "+cats).lower()
      # require exact binomial words somewhere in metadata/title
      words=tar["name"].lower().split()
      if not all(w in hay for w in words): continue
      lic=clean(m.get("LicenseShortName","")); url=ii.get("url")
      if not url or not lic: continue
      score=0
      for kw,w in [("uproot",8),("harvest",8),("picked",8),("plucked",8),("fallen",4),("root",4),("whole plant",5),("medicinal",3),("market",4),("food",2),("vegetable",2),("dried",8),("dry",5),("leaf",1),("flower",1)]:
        if kw in hay: score+=w
      if "herbarium" in hay: score-=20
      if "illustration" in hay or title.lower().endswith((".svg",".pdf",".djvu")): score-=15
      key=title
      rec={"title":title,"pageid":p.get("pageid"),"description":desc,"categories":cats,
           "author":clean(m.get("Artist","")),"credit":clean(m.get("Credit","")),
           "license":lic,"license_url":clean(m.get("LicenseUrl","")),"usage_terms":clean(m.get("UsageTerms","")),
           "url":url,"sha1":ii.get("sha1"),"width":ii.get("width"),"height":ii.get("height"),"size":ii.get("size"),"score":score}
      if key not in pool or score>pool[key]["score"]: pool[key]=rec
  top=sorted(pool.values(),key=lambda x:(-x["score"],x["title"]))[:12]
  thumbs=[]
  for idx,rec in enumerate(top):
    try:
      # request thumb max 700 px via imageinfo thumburl
      p=get({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|sha1|extmetadata",
             "iiurlwidth":700,"titles":rec["title"]})
      pg=next(iter(p["query"]["pages"].values())); ii=pg["imageinfo"][0]
      tu=ii.get("thumburl") or ii.get("url")
      rr=s.get(tu,timeout=120); rr.raise_for_status()
      im=Image.open(io.BytesIO(rr.content)).convert("RGB")
      fn=OUT/f'{tar["id"]:03d}_{idx+1:02d}.jpg'; im.save(fn,quality=90)
      rec["thumb_file"]=str(fn); rec["thumb_width"]=im.width; rec["thumb_height"]=im.height; rec["thumb_sha256"]=sha256(fn.read_bytes())
      thumbs.append((im,rec))
    except Exception as e:
      rec["thumb_error"]=repr(e)
  allrows[str(tar["id"])]={"target":tar,"candidates":top}
  # contact sheet
  if thumbs:
    cellw,cellh=760,610; cols=2; rows=math.ceil(len(thumbs)/cols)
    sheet=Image.new("RGB",(cellw*cols,cellh*rows),"white"); dr=ImageDraw.Draw(sheet)
    for k,(im,rec) in enumerate(thumbs):
      x=(k%cols)*cellw; y=(k//cols)*cellh
      thumb=ImageOps.contain(im,(720,460)); sheet.paste(thumb,(x+20,y+20))
      label=f'{tar["id"]} cand {k+1} score {rec["score"]}: {rec["title"]}'
      dr.text((x+20,y+490),label[:100],fill="black")
      dr.text((x+20,y+515),("lic: "+rec["license"])[:100],fill="black")
      dr.text((x+20,y+540),("desc: "+rec["description"])[:110],fill="black")
    sheet.save(OUT/f'contact_{tar["id"]:03d}.jpg',quality=88)
  print("TARGET",tar["id"],json.dumps(top,ensure_ascii=False),flush=True)
(OUT/"manifest.json").write_text(json.dumps(allrows,ensure_ascii=False,indent=2),encoding="utf-8")
