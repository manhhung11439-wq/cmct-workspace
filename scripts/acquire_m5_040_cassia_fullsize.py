import hashlib,json,pathlib,time,requests
from PIL import Image
from io import BytesIO
OUT=pathlib.Path("evidence/m5_t1_040_cassia_fullsize"); OUT.mkdir(parents=True,exist_ok=True)
urls=[
"https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41598-022-12748-7/MediaObjects/41598_2022_12748_Fig1_HTML.png",
"https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fs41598-022-12748-7/MediaObjects/41598_2022_12748_Fig1_HTML.png"
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/6.2 Cassia tora full-size figure"
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
got=[]
for u in urls:
    try:
        r=s.get(u,timeout=180,allow_redirects=True); r.raise_for_status()
        data=r.content; im=Image.open(BytesIO(data)); im.load()
        p=OUT/f"figure1_{len(got)+1}.{(im.format or 'PNG').lower().replace('jpeg','jpg')}"; p.write_bytes(data)
        s1,s256=hh(data)
        got.append({"requested_url":u,"resolved_url":r.url,"file":str(p),"bytes":len(data),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
    except Exception as e:
        got.append({"requested_url":u,"error":repr(e)})
if not any("file" in x for x in got): raise RuntimeError("no full-size figure acquired")
(OUT/"manifest.json").write_text(json.dumps(got,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(got,ensure_ascii=False))
