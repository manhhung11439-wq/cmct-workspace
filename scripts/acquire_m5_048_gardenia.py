import requests,pathlib,json,hashlib,time
OUT=pathlib.Path("evidence/m5_t1_048_gardenia"); OUT.mkdir(parents=True,exist_ok=True)
url="https://www.frontiersin.org/files/Articles/1712973/xml-images/fsufs-09-1712973-g001.webp"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.6 exact Gardenia processed-fruit figure"
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(30,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
r=get(url); data=r.content
if len(data)<10000: raise RuntimeError("unexpected small image")
p=OUT/"gardenia_fig1_original.webp"; p.write_bytes(data)
s1=hashlib.sha1(data).hexdigest(); s256=hashlib.sha256(data).hexdigest()
manifest={
 "id":48,
 "doi":"10.3389/fsufs.2025.1712973",
 "article":"Chai C, Jin B, Cui Y, Cui X, Shan C, Yu S, Wen H. Frontiers in Sustainable Food Systems. Published 30 Jan 2026.",
 "identity":"Gardenia jasminoides J.Ellis",
 "article_material":"dried mature fruit of Gardenia jasminoides J.Ellis",
 "processing":"remove stalks/impurities; steam 10-15 min; dry at 60 C",
 "figure_interpretation":"Figure 1 top row = fresh unprocessed fruits stages 1-7; bottom row = processed dried medicinal herbs from corresponding stages",
 "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
 "figure_url":r.url,"file":str(p),"bytes":len(data),"sha1":s1,"sha256":s256
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_048_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
