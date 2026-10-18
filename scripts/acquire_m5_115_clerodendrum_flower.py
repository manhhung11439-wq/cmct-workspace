import json,hashlib,pathlib,time,requests,html,re
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_115_clerodendrum_flower"); OUT.mkdir(parents=True,exist_ok=True)
TITLE="File:Chendu mulla flower from Kottayam.jpg"
POWO="https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:862311-1"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/34.0 Clerodendrum chinense fresh-flower acquisition"
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
q=get("https://commons.wikimedia.org/w/api.php",{
 "action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","titles":TITLE
}).json()
p=next(iter(q["query"]["pages"].values())); ii=p["imageinfo"][0]; meta=ii.get("extmetadata",{})
b=get(ii["url"]).content
fn=OUT/"m5_115_Clerodendrum_chinense_fresh_harvested_flowers.jpg"; fn.write_bytes(b)
im=Image.open(fn); im.load(); s1,s256=hh(b)
assert s1==ii.get("sha1"),(s1,ii.get("sha1"))
# Taxonomic synonym basis from Kew POWO.
pr=get(POWO); pt=pr.text
(OUT/"powo_synonym.html").write_text(pt,encoding="utf-8",errors="ignore")
plain=re.sub(r"<[^>]+>"," ",html.unescape(pt))
plain=" ".join(plain.split())
syn_ok=("Clerodendrum philippinum" in plain and "synonym of Clerodendrum chinense" in plain)
rec={
 "id":115,
 "target":"Bạch Đồng Nữ / Clerodendrum chinense (Osbeck) Mabb.",
 "source_name":"Clerodendrum philippinum Schauer",
 "taxon_synonym_basis":{"url":POWO,"confirmed":syn_ok,
   "statement":"Plants of the World Online: Clerodendrum philippinum Schauer is a synonym of Clerodendrum chinense (Osbeck) Mabb."},
 "title":TITLE,"canonical_title":p.get("title"),"pageid":p.get("pageid"),
 "original_url":ii["url"],"api_sha1":ii.get("sha1"),"local_sha1":s1,"local_sha256":s256,
 "bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"file":str(fn),
 "description":clean(meta.get("ImageDescription","")),"author":clean(meta.get("Artist","")),
 "credit":clean(meta.get("Credit","")),"license_short":clean(meta.get("LicenseShortName","")),
 "license_url":clean(meta.get("LicenseUrl","")),"usage_terms":clean(meta.get("UsageTerms","")),
 "copyrighted":clean(meta.get("Copyrighted","")),"categories":clean(meta.get("Categories","")),
 "manuscript_role":"§115.1 includes flowers among used parts; §115.5 permits fresh use. Visual controller must confirm detached harvested flower cluster.",
 "controller_status":"ORIGINAL + TAXON SYNONYM CHAIN ACQUIRED; VISUAL LOCK REQUIRED BEFORE PROMOTION"
}
(OUT/"manifest.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(rec,ensure_ascii=False),flush=True)
