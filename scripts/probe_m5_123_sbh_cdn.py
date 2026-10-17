import json,hashlib,pathlib,time,requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_123_sbh_cdn"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/32.1 SBH original CDN probe"
urls=[
 "https://cdn.ncbi.nlm.nih.gov/pmc/blobs/65b4/6280310/f6ca778e22b2/ECAM2018-4365739.001.jpg",
 "https://pmc.ncbi.nlm.nih.gov/articles/PMC6280310/bin/ECAM2018-4365739.001.jpg"
]
def get(u):
    last=None
    for i in range(6):
        r=s.get(u,timeout=120,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(30,2*(2**i))); continue
        if r.status_code>=400: return r
        return r
    return last
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
rows=[]
for i,u in enumerate(urls,1):
    r=get(u)
    rec={"url":u,"status":r.status_code,"final":r.url,"content_type":r.headers.get("content-type"),"bytes":len(r.content)}
    if r.ok:
        try:
            p=OUT/f"candidate_{i}.jpg"; p.write_bytes(r.content)
            im=Image.open(p); im.load()
            s1,s256=hh(r.content)
            rec.update({"file":str(p),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
        except Exception as e:
            rec["image_error"]=repr(e)
    rows.append(rec); print(json.dumps(rec,ensure_ascii=False),flush=True)
(OUT/"manifest.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
