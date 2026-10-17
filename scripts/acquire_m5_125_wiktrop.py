import json,hashlib,pathlib,time,requests
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_125_wiktrop"); OUT.mkdir(parents=True,exist_ok=True)
pages=[
"https://portal.wiktrop.org/fr/observation/show/479670",
"https://portal.wiktrop.org/observation/show/479663",
"https://portal.wiktrop.org/group/Malherbologie-Weed_Science/observation/show/9393",
"https://portal.wiktrop.org/observation/show/8541",
"https://portal.wiktrop.org/observation/show/14384",
"https://portal.wiktrop.org/observation/show/5144",
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/31.0 Scoparia dulcis WIKTROP screen"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=120,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(30,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
rows=[]
for pi,page in enumerate(pages,1):
    pr=get(page); hb=pr.content
    (OUT/f"obs_{pi:02d}.html").write_bytes(hb)
    soup=BeautifulSoup(pr.text,"html.parser")
    nd=soup.find("script",id="__NEXT_DATA__")
    if not nd: 
        print("NO_NEXT_DATA",page,flush=True); continue
    data=json.loads(nd.string)
    pp=data["props"]["pageProps"]["observation"]
    obs=pp.get("observation",{}).get("observation",{})
    resources=pp.get("observationResource",[])
    for entry in resources:
        res=entry.get("resource",{}); lic=entry.get("license") or {}; user=entry.get("userIbp") or {}
        fn=res.get("fileName") or ""
        if not fn: continue
        raw="https://portal.wiktrop.org/files-api/api/get/raw/observations/"+fn
        raw=raw.replace("/observations//","/observations/")
        try:
            ir=get(raw); b=ir.content
            im=Image.open(__import__("io").BytesIO(b)); im.load()
        except Exception as e:
            print("ERR",page,fn,repr(e),flush=True); continue
        ext="."+((im.format or "JPEG").lower().replace("jpeg","jpg"))
        p=OUT/f"obs{pi:02d}_res{res.get('id','x')}{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        row={"target":"Scoparia dulcis L.","observation_page":page,"observation_id":obs.get("id"),
             "resource_id":res.get("id"),"fileName":fn,"raw_url":ir.url,
             "author_name":user.get("name"),"contributor":res.get("contributor"),"uploaderId":res.get("uploaderId"),
             "license_id":lic.get("id"),"license_name":lic.get("name"),"license_url":lic.get("url"),
             "file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,
             "sha1":s1,"sha256":s256}
        rows.append(row); print("ROW="+json.dumps(row,ensure_ascii=False),flush=True)
(OUT/"manifest.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
thumbs=[]
for i,row in enumerate(rows,1):
    try:
        im=Image.open(row["file"]).convert("RGB"); im.thumbnail((300,220))
    except: continue
    tile=Image.new("RGB",(330,285),"white"); tile.paste(im,((330-im.width)//2,5))
    d=ImageDraw.Draw(tile)
    d.text((8,230),f"{i}: obs{row['observation_id']} res{row['resource_id']}\n{row['license_name']} {row['width']}x{row['height']}",fill="black")
    thumbs.append(tile)
if thumbs:
    cols=4; rn=(len(thumbs)+cols-1)//cols
    sheet=Image.new("RGB",(cols*330,rn*285),"white")
    for i,t in enumerate(thumbs): sheet.paste(t,((i%cols)*330,(i//cols)*285))
    sheet.save(OUT/"contact.jpg",quality=90)
print("TOTAL",len(rows),flush=True)
