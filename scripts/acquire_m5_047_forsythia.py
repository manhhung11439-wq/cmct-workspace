import requests,pathlib,json,hashlib,time
OUT=pathlib.Path("evidence/m5_t1_047_forsythia"); OUT.mkdir(parents=True,exist_ok=True)
url="https://www.frontiersin.org/files/Articles/758326/xml-images/fgene-12-758326-g001.webp"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.4 exact Forsythiae Fructus figure"
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
p=OUT/"forsythia_fig1_original.webp"; p.write_bytes(data)
s1=hashlib.sha1(data).hexdigest(); s256=hashlib.sha256(data).hexdigest()
manifest={"id":47,"doi":"10.3389/fgene.2021.758326",
 "article":"Wu B, Li Y, Zhao W, Meng Z, Ji W, Wang C. Frontiers in Genetics 2021;12:758326",
 "caption":"Figure 1. (A) Forsythia suspensa (Thunb.) Vahl; (B) Forsythia fruit growing on the tree; (C) Forsythiae Fructus as a medicinal material.",
 "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
 "figure_url":r.url,"file":str(p),"bytes":len(data),"sha1":s1,"sha256":s256}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_047_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
