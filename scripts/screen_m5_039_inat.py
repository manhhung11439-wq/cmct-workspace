import pathlib,requests,time,json,hashlib,math
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_039_inat_exact"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/39.0 exact Scleromitrion diffusum iNat screen"
OK={"cc0","cc-by","cc-by-sa"}
def get(u,params=None):
  last=None
  for i in range(8):
    r=s.get(u,params=params,timeout=180); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(60,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
# Resolve exact accepted taxon
taxa=get("https://api.inaturalist.org/v1/taxa/autocomplete",{"q":"Scleromitrion diffusum","per_page":20}).json()["results"]
tax=next((x for x in taxa if x.get("rank")=="species" and x.get("name")=="Scleromitrion diffusum"),None)
if not tax:
  taxa2=get("https://api.inaturalist.org/v1/taxa/autocomplete",{"q":"Hedyotis diffusa","per_page":20}).json()["results"]
  tax=next((x for x in taxa2 if x.get("rank")=="species" and x.get("name") in ("Scleromitrion diffusum","Hedyotis diffusa")),None)
if not tax: raise RuntimeError("exact taxon unresolved "+json.dumps(taxa[:5],ensure_ascii=False))
tid=tax["id"]
rows=[]; seen=set()
for page in range(1,9):
  js=get("https://api.inaturalist.org/v1/observations",{
    "taxon_id":tid,"photos":"true","quality_grade":"research,needs_id,casual",
    "per_page":100,"page":page,"order_by":"created_at","order":"desc"
  }).json()
  for o in js.get("results",[]):
    for p in o.get("photos",[]):
      lic=(p.get("license_code") or "").lower()
      if lic not in OK: continue
      pid=p.get("id")
      if pid in seen: continue
      seen.add(pid)
      url=p.get("url")
      if not url: continue
      # iNat replace square with medium/large/original
      large=url.replace("square","large")
      original=url.replace("square","original")
      try:
        b=get(large).content
        fn=OUT/f"obs{o['id']}_photo{pid}.jpg"; fn.write_bytes(b)
        im=Image.open(fn); im.load()
      except Exception:
        continue
      rows.append({
        "obs_id":o.get("id"),"photo_id":pid,"license":lic,
        "attribution":p.get("attribution"),"large_url":large,"original_url":original,
        "observed_on":o.get("observed_on"),"place_guess":o.get("place_guess"),
        "description":o.get("description"),"taxon_id":tid,"taxon_name":tax.get("name"),
        "file":str(fn),"width":im.width,"height":im.height
      })
  if len(js.get("results",[]))<100: break
# contact sheets max 36 each
thumbs=[]
for r in rows:
  im=Image.open(r["file"]).convert("RGB")
  tile=Image.new("RGB",(300,250),"white")
  fit=ImageOps.contain(im,(280,190)); tile.paste(fit,((300-fit.width)//2,5))
  d=ImageDraw.Draw(tile)
  txt=f"obs {r['obs_id']} p{r['photo_id']} {r['license']}\n{(r.get('description') or '')[:55]}"
  d.multiline_text((8,200),txt,fill="black",spacing=2)
  thumbs.append(tile)
for start in range(0,len(thumbs),36):
  chunk=thumbs[start:start+36]; cols=6; rowsn=math.ceil(len(chunk)/cols)
  sheet=Image.new("RGB",(cols*300,rowsn*250),"white")
  for i,t in enumerate(chunk): sheet.paste(t,((i%cols)*300,(i//cols)*250))
  sheet.save(OUT/f"contact_{start//36+1:02d}.jpg",quality=88)
(OUT/"manifest.json").write_text(json.dumps({"taxon":tax,"candidates":rows},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"taxon_id":tid,"taxon_name":tax.get("name"),"reusable_photos":len(rows),"contacts":math.ceil(len(rows)/36)},ensure_ascii=False),flush=True)
