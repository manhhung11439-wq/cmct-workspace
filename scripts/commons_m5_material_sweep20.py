import json,time,requests,pathlib,re,html
OUT=pathlib.Path("evidence/m5_t1_commons_sweep20"); OUT.mkdir(parents=True,exist_ok=True)
targets=[
 (68,"Phyllostachys nigra dried leaves"),
 (82,"Houttuynia cordata dried herb"),
 (83,"Ageratum conyzoides dried herb"),
 (85,"Euphorbia thymifolia dried herb"),
 (89,"Excoecaria cochinchinensis leaves"),
 (92,"Eleusine indica dried herb"),
 (93,"Bidens pilosa dried herb"),
 (104,"Platostoma palustre dried herb"),
 (106,"Glinus oppositifolius herb"),
 (112,"Pteris multifida dried herb"),
 (113,"Peristrophe bivalvis leaves"),
 (115,"Clerodendrum chinense leaves"),
 (116,"Acanthus ilicifolius dried"),
 (117,"Commelina communis harvested"),
 (118,"Barleria lupulina leaves"),
 (119,"Breynia fruticosa leaves"),
 (120,"Ludwigia hyssopifolia herb"),
 (123,"Scutellaria barbata dried herb"),
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/20.2 commons medicinal-material sweep"
def get(params):
  last=None
  for i in range(8):
    r=s.get("https://commons.wikimedia.org/w/api.php",params=params,timeout=180); last=r
    if r.status_code in (429,500,502,503,504): time.sleep(min(60,2*(2**i))); continue
    r.raise_for_status(); return r.json()
  last.raise_for_status()
def clean(v):
  if isinstance(v,dict): v=v.get("value","")
  return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()
out={}
for rid,q in targets:
  data=get({"action":"query","format":"json","generator":"search","gsrsearch":q,"gsrnamespace":6,"gsrlimit":20,
            "prop":"imageinfo","iiprop":"url|size|sha1|extmetadata"})
  rows=[]
  for p in (data.get("query",{}).get("pages",{}) or {}).values():
    ii=(p.get("imageinfo") or [{}])[0]; m=ii.get("extmetadata",{})
    row={"title":p.get("title"),"pageid":p.get("pageid"),"width":ii.get("width"),"height":ii.get("height"),
         "sha1":ii.get("sha1"),"url":ii.get("url"),"description":clean(m.get("ImageDescription","")),
         "author":clean(m.get("Artist","")),"license":clean(m.get("LicenseShortName","")),
         "license_url":clean(m.get("LicenseUrl","")),"categories":clean(m.get("Categories",""))}
    rows.append(row)
  out[str(rid)]={"query":q,"results":rows}
  print("TARGET",rid,q,"RESULTS",len(rows),flush=True)
  for x in rows[:10]: print(json.dumps(x,ensure_ascii=False),flush=True)
(OUT/"search_results.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
