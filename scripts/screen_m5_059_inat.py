import pathlib,requests,time,json,math
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_059_inat_exact"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/59.0 exact Callisia fragrans detached screen"
OK={"cc0","cc-by","cc-by-sa"}
def get(u,params=None):
  last=None
  for i in range(8):
    r=s.get(u,params=params,timeout=180); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(60,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
taxa=get("https://api.inaturalist.org/v1/taxa/autocomplete",{"q":"Callisia fragrans","per_page":20}).json()["results"]
tax=next((x for x in taxa if x.get("rank")=="species" and x.get("name")=="Callisia fragrans"),None)
if not tax: raise RuntimeError("taxon unresolved")
tid=tax["id"]; rows=[]; seen=set()
for page in range(1,11):
  js=get("https://api.inaturalist.org/v1/observations",{"taxon_id":tid,"photos":"true","per_page":100,"page":page,"order_by":"created_at","order":"desc"}).json()
  for o in js.get("results",[]):
    for p in o.get("photos",[]):
      lic=(p.get("license_code") or "").lower()
      if lic not in OK or p.get("id") in seen: continue
      seen.add(p.get("id")); url=p.get("url")
      if not url: continue
      large=url.replace("square","large"); original=url.replace("square","original")
      try:
        b=get(large).content; fn=OUT/f"obs{o['id']}_photo{p['id']}.jpg"; fn.write_bytes(b)
        im=Image.open(fn); im.load()
      except: continue
      rows.append({"obs_id":o["id"],"photo_id":p["id"],"license":lic,"attribution":p.get("attribution"),
                   "large_url":large,"original_url":original,"description":o.get("description"),"place_guess":o.get("place_guess"),
                   "file":str(fn),"width":im.width,"height":im.height})
  if len(js.get("results",[]))<100: break
tiles=[]
for r in rows:
  im=Image.open(r["file"]).convert("RGB"); tile=Image.new("RGB",(300,250),"white")
  fit=ImageOps.contain(im,(280,190)); tile.paste(fit,((300-fit.width)//2,5))
  d=ImageDraw.Draw(tile); d.multiline_text((8,200),f"obs {r['obs_id']} p{r['photo_id']} {r['license']}\n{(r.get('description') or '')[:55]}",fill="black",spacing=2); tiles.append(tile)
for start in range(0,len(tiles),36):
  ch=tiles[start:start+36]; sh=Image.new("RGB",(1800,math.ceil(len(ch)/6)*250),"white")
  for i,t in enumerate(ch): sh.paste(t,((i%6)*300,(i//6)*250))
  sh.save(OUT/f"contact_{start//36+1:02d}.jpg",quality=88)
(OUT/"manifest.json").write_text(json.dumps({"taxon":tax,"candidates":rows},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"taxon_id":tid,"reusable":len(rows),"contacts":math.ceil(len(rows)/36)},ensure_ascii=False))
