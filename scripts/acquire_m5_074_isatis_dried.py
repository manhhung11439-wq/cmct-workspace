import re,json,hashlib,pathlib,time,requests,urllib.parse
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_074_isatis_dried_leaves"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/24.2 Isatis dried-leaf figure acquisition"
urls=[
 "https://www.mdpi.com/2571-9408/7/2/42",
 "https://www.mdpi.com/2571-9408/7/2/42/xml",
 "https://www.mdpi.com/2571-9408/7/2/42/pdf",
]
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=180,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(60,2*(2**i))); continue
    return r
  return last
seen=[]; candidates=[]
for u in list(urls):
  r=get(u); seen.append({"url":u,"status":r.status_code,"final":r.url,"ct":r.headers.get("content-type"),"bytes":len(r.content)})
  if r.ok and ("html" in (r.headers.get("content-type") or "") or "xml" in (r.headers.get("content-type") or "")):
    txt=r.text; (OUT/f"page_{len(seen)}.txt").write_text(txt,encoding="utf-8",errors="ignore")
    for m in re.findall(r'''(?:src|href)=["']([^"']*(?:g002|figure-2)[^"']*)["']''',txt,re.I):
      uu=urllib.parse.urljoin(r.url,m.replace("&amp;","&"))
      if uu not in candidates: candidates.append(uu)
# Known MDPI patterns fallback
for base in ["https://mdpi-res.com/d_attachment/heritage/heritage-07-00042/article_deploy/html/images/",
             "https://pub.mdpi-res.com/heritage/heritage-07-00042/article_deploy/html/images/"]:
  for fn in ["heritage-07-00042-g002.png","heritage-07-00042-g002.jpg","heritage-07-00042-g002-550.jpg"]:
    u=base+fn
    if u not in candidates: candidates.append(u)
assets=[]
for u in candidates:
  try:
    r=get(u)
    if not r.ok: continue
    ct=r.headers.get("content-type") or ""
    if not ct.startswith("image/"): continue
    ext=".png" if "png" in ct else ".jpg"
    p=OUT/f"figure2_original_{len(assets)+1}{ext}"; p.write_bytes(r.content)
    im=Image.open(p); im.load()
    b=r.content
    assets.append({"url":u,"final":r.url,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,
      "sha1":hashlib.sha1(b).hexdigest(),"sha256":hashlib.sha256(b).hexdigest()})
  except Exception as e: pass
# caption/licensing evidence from HTML if available
page=""
for p in OUT.glob("page_*.txt"):
  t=p.read_text(encoding="utf-8",errors="ignore")
  if "dried leaves of the Isatis tinctoria plant" in t:
    page=t; break
snippet=""
needle="dried leaves of the Isatis tinctoria plant"
i=page.find(needle)
if i>=0: snippet=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",page[max(0,i-1800):i+1800])).strip()
man={"id":74,"target":"Đại Thanh Diệp / Isatis tinctoria L. / dried leaves",
 "article":"Domesticating Colour in the Early Modern Age: Dyeing Wool in Black in Portugal",
 "article_url":"https://www.mdpi.com/2571-9408/7/2/42",
 "figure2_caption_evidence":snippet,
 "source_photo_license_from_caption":"CC BY-SA 4.0 DEED; photo by Frédéric Neupont",
 "requests":seen,"candidate_urls":candidates,"assets":assets,
 "controller_status":"ASSET_ACQUIRED if assets nonempty; crop dried-leaf region only after visual lock"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(man,ensure_ascii=False,indent=2),flush=True)
if not assets: raise RuntimeError("No Figure 2 image asset acquired")
