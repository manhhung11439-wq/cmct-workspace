import requests,json,pathlib,time,hashlib,re,html
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_062_wikipedia_food_image"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/62.0 Paederia Wikipedia media resolver"
def get(u,params=None):
  last=None
  for i in range(8):
    r=s.get(u,params=params,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(60,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
def clean(v):
  if isinstance(v,dict): v=v.get("value","")
  return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
api="https://en.wikipedia.org/w/api.php"
js=get(api,{"action":"query","format":"json","prop":"images","titles":"Paederia lanuginosa","imlimit":"max"}).json()
page=next(iter(js["query"]["pages"].values()))
titles=[x["title"] for x in page.get("images",[])]
print("IMAGES",json.dumps(titles,ensure_ascii=False),flush=True)
candidates=[]
for title in titles:
  q=get("https://commons.wikimedia.org/w/api.php",{
    "action":"query","format":"json","prop":"imageinfo",
    "iiprop":"url|size|sha1|extmetadata","titles":title
  }).json()
  p=next(iter(q["query"]["pages"].values()))
  if "imageinfo" not in p: continue
  ii=p["imageinfo"][0]; meta=ii.get("extmetadata",{})
  rec={"title":title,"pageid":p.get("pageid"),"url":ii.get("url"),"width":ii.get("width"),"height":ii.get("height"),"sha1":ii.get("sha1"),
       "description":clean(meta.get("ImageDescription","")),"author":clean(meta.get("Artist","")),"credit":clean(meta.get("Credit","")),
       "license_short":clean(meta.get("LicenseShortName","")),"license_url":clean(meta.get("LicenseUrl","")),
       "categories":clean(meta.get("Categories",""))}
  candidates.append(rec)
  print("META",json.dumps(rec,ensure_ascii=False),flush=True)
  # download files whose metadata looks like food/nem/Paederia
  blob=" ".join([rec["title"],rec["description"],rec["categories"]]).lower()
  if any(k in blob for k in ["nem","food","cuisine","paederia","mơ","mo long","lá mơ","la mo"]):
    try:
      b=get(rec["url"]).content
      ext=pathlib.Path(rec["url"].split("?")[0]).suffix or ".jpg"
      fn=OUT/(re.sub(r"[^A-Za-z0-9_.-]+","_",title.replace("File:",""))[:120]+ext)
      fn.write_bytes(b); im=Image.open(fn); im.load()
      s1,s256=hh(b)
      rec.update({"file":str(fn),"local_sha1":s1,"local_sha256":s256,"bytes":len(b),"local_width":im.width,"local_height":im.height})
    except Exception as e: rec["download_error"]=repr(e)
(OUT/"manifest.json").write_text(json.dumps({"page_images":titles,"candidates":candidates},ensure_ascii=False,indent=2),encoding="utf-8")
