import requests,pathlib,json,hashlib,time
OUT=pathlib.Path("evidence/m5_t1_044_coptis"); OUT.mkdir(parents=True,exist_ok=True)
article="https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0153127"
figurl="https://journals.plos.org/plosone/article/figure/image?size=large&id=10.1371/journal.pone.0153127.g001"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.2 exact Coptis dried-rhizome figure"
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(30,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
r=get(figurl); data=r.content
ct=(r.headers.get("content-type") or "").lower()
if len(data)<10000: raise RuntimeError("unexpected small figure")
ext=".png" if "png" in ct else ".jpg" if ("jpeg" in ct or "jpg" in ct) else ".bin"
p=OUT/("coptis_fig1_original"+ext); p.write_bytes(data)
s1=hashlib.sha1(data).hexdigest(); s256=hashlib.sha256(data).hexdigest()
manifest={
 "id":44,
 "article_url":article,
 "doi":"10.1371/journal.pone.0153127",
 "figure_id":"g001",
 "caption":"Fig 1. Coptis chinensis. A, plants; B, dried rhizome (Rhizoma Coptidis); C, carpels.",
 "figure_url":r.url,
 "content_type":ct,
 "original_file":str(p),
 "bytes":len(data),
 "sha1":s1,
 "sha256":s256,
 "license":"CC BY (PLOS ONE open-access license)"
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_044_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
