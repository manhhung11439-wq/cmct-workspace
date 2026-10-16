import json,hashlib,pathlib,time,requests,html,re
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_025_douchi"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/8.0 exact Douchi acquisition"
files=[
 "File:2015 1012 Preserved black beans douchi close-up.jpg",
 "File:Douchiphoto.jpg",
]
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
items=[]
for i,title in enumerate(files,1):
    q=get("https://commons.wikimedia.org/w/api.php",{
      "action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","titles":title
    }).json()
    p=next(iter(q["query"]["pages"].values()))
    ii=p["imageinfo"][0]; meta=ii.get("extmetadata",{})
    url=ii["url"]; b=get(url).content
    ext=pathlib.Path(url.split("?")[0]).suffix or ".jpg"
    fn=OUT/f"candidate_{i:02d}{ext}"; fn.write_bytes(b)
    im=Image.open(fn); im.load()
    s1,s256=hh(b)
    rec={
      "title":title,"pageid":p.get("pageid"),"canonical_title":p.get("title"),"original_url":url,
      "api_sha1":ii.get("sha1"),"local_sha1":s1,"local_sha256":s256,"bytes":len(b),
      "width":im.width,"height":im.height,"format":im.format,"file":str(fn),
      "description":clean(meta.get("ImageDescription","")),
      "author":clean(meta.get("Artist","")),
      "credit":clean(meta.get("Credit","")),
      "license_short":clean(meta.get("LicenseShortName","")),
      "license_url":clean(meta.get("LicenseUrl","")),
      "usage_terms":clean(meta.get("UsageTerms","")),
      "copyrighted":clean(meta.get("Copyrighted","")),
      "categories":clean(meta.get("Categories","")),
      "date_time_original":clean(meta.get("DateTimeOriginal","")),
    }
    items.append(rec)
    print("CANDIDATE="+json.dumps(rec,ensure_ascii=False),flush=True)

# Persist a scientific identity chain from Europe PMC.
pmc="PMC6571576"
xr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML")
xb=xr.content; (OUT/"pmc6571576_fulltext.xml").write_bytes(xb)
science={"pmc":pmc,"url":xr.url,"bytes":len(xb),"sha1":hh(xb)[0],"sha256":hh(xb)[1],
         "identity_statement":"Sojae semen praeparatum (dandouchi) is a Chinese fermented preparation obtained from ripe seed of soybean Glycine max (L.) Merr.; article full text persisted for controller verification."}
manifest={"id":25,"target":"Đạm Đậu Sị / Sojae Semen Praeparatum / Glycine max (L.) Merr.","commons_candidates":items,"scientific_identity":science,
          "controller_rule":"No promotion unless the image itself shows standalone fermented black beans/douchi and file-level reusable rights are explicit."}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
