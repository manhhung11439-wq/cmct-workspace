import requests,pathlib,hashlib,json,time
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_101_paris2025"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/11.1 Paris polyphylla Figshare acquisition"
article_id=29307142
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
meta=get(f"https://api.figshare.com/v2/articles/{article_id}").json()
(OUT/"figshare_article_metadata.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
files=meta.get("files",[])
pick=None
for f in files:
    n=(f.get("name") or "").lower()
    if "graphical" in n and (n.endswith(".tif") or n.endswith(".tiff") or n.endswith(".png") or n.endswith(".jpg") or n.endswith(".jpeg")):
        pick=f;break
if pick is None: raise RuntimeError(f"Graphical abstract file not found: {[f.get('name') for f in files]}")
url=pick.get("download_url")
b=get(url).content
suffix=pathlib.Path(pick["name"]).suffix or ".tiff"
p=OUT/("graphical_abstract_original"+suffix); p.write_bytes(b)
im=Image.open(p); im.load()
sha1=hashlib.sha1(b).hexdigest(); sha256=hashlib.sha256(b).hexdigest()
man={"id":101,"target":"Thất Diệp Nhất Chi Hoa / Paris polyphylla Sm. / rhizome",
     "article":"Tran TG et al. Cogent Food & Agriculture 2025;11:2518217",
     "doi":"10.1080/23311932.2025.2518217",
     "figshare_article_id":article_id,
     "figshare_url":meta.get("url_private_api") or meta.get("url"),
     "figshare_title":meta.get("title"),"figshare_license":meta.get("license"),
     "file_record":pick,"original_file":str(p),"bytes":len(b),"width":im.width,"height":im.height,
     "format":im.format,"sha1":sha1,"sha256":sha256,
     "article_role":"Study explicitly prepares Paris polyphylla Smith rhizomes under drying conditions; graphical abstract depicts detached rhizomes in the drying workflow.",
     "controller_status":"ORIGINAL GRAPHICAL ABSTRACT ACQUIRED; RHIZOME CROP REQUIRES VISUAL LOCK"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
