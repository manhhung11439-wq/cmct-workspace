import json,hashlib,pathlib,time,requests,html,re
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_092_eleusine"); OUT.mkdir(parents=True,exist_ok=True)
TITLE="File:Goosegrass (18843732861).jpg"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/23.0 Eleusine indica whole-plant acquisition"
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
q=get("https://commons.wikimedia.org/w/api.php",params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","titles":TITLE}).json()
p=next(iter(q["query"]["pages"].values())); ii=p["imageinfo"][0]; m=ii.get("extmetadata",{})
b=get(ii["url"]).content; fn=OUT/"m5_092_Eleusine_indica_whole_plant.jpg"; fn.write_bytes(b)
im=Image.open(fn); im.load(); s1,s256=hh(b); assert s1==ii.get("sha1")
man={"id":92,"target":"Cỏ Mần Trầu / Eleusine indica (L.) Gaertn.","title":TITLE,"pageid":p.get("pageid"),
"original_url":ii["url"],"api_sha1":ii.get("sha1"),"sha1":s1,"sha256":s256,"bytes":len(b),
"width":im.width,"height":im.height,"format":im.format,"file":str(fn),
"description":clean(m.get("ImageDescription","")),"author":clean(m.get("Artist","")),"credit":clean(m.get("Credit","")),
"license":clean(m.get("LicenseShortName","")),"license_url":clean(m.get("LicenseUrl","")),"usage_terms":clean(m.get("UsageTerms","")),
"categories":clean(m.get("Categories","")),
"manuscript_role":"§92.5 uses the whole plant with roots, fresh or dried. Promotion requires visual confirmation that the photographed whole plant is detached/uprooted rather than growing in situ.",
"controller_status":"ORIGINAL_ACQUIRED; VISUAL LOCK REQUIRED"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(man,ensure_ascii=False,indent=2),flush=True)
