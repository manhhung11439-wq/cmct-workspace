import json,hashlib,pathlib,time,requests,html,re
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_090_sauropus_pd"); OUT.mkdir(parents=True,exist_ok=True)
TITLE="File:SauropusAndrogynus.jpg"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/25.0 Sauropus exact PD candidate"
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
q=get("https://commons.wikimedia.org/w/api.php",{"action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","titles":TITLE}).json()
p=next(iter(q["query"]["pages"].values())); ii=p["imageinfo"][0]; meta=ii.get("extmetadata",{})
b=get(ii["url"]).content
fn=OUT/"m5_090_SauropusAndrogynus_PD.jpg"; fn.write_bytes(b)
im=Image.open(fn); im.load(); s1,s256=hh(b)
rec={"id":90,"target":"Rau Ngót / Sauropus androgynus (syn. Phyllanthus androgynus)",
"title":TITLE,"pageid":p.get("pageid"),"original_url":ii["url"],"api_sha1":ii.get("sha1"),"local_sha1":s1,"local_sha256":s256,
"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"file":str(fn),
"description":clean(meta.get("ImageDescription","")),"author":clean(meta.get("Artist","")),"credit":clean(meta.get("Credit","")),
"license_short":clean(meta.get("LicenseShortName","")),"license_url":clean(meta.get("LicenseUrl","")),"usage_terms":clean(meta.get("UsageTerms","")),
"categories":clean(meta.get("Categories","")),"controller_status":"VISUAL LOCK REQUIRED — determine detached harvested shoots vs living/growing plant"}
assert s1==ii.get("sha1")
(OUT/"manifest.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(rec,ensure_ascii=False),flush=True)
