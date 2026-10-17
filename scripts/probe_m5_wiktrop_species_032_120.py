import json,pathlib,requests,time,re,hashlib,io
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_wiktrop_species_probe_032_120"); OUT.mkdir(parents=True,exist_ok=True)
targets={
  32:{"species_id":803,"target":"Kyllinga nemoralis (J.R.Forst. & G.Forst.) Dandy ex Hutch. & Dalziel"},
  120:{"species_id":535,"target":"Ludwigia hyssopifolia (G.Don) Exell"},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/33.2 WIKTROP species media probe"
def get(u):
    last=None
    for i in range(5):
        try:
            r=s.get(u,timeout=35,allow_redirects=True); last=r
        except requests.RequestException as e:
            last=e
            time.sleep(min(15,2*(2**i)))
            continue
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(15,2*(2**i))); continue
        if r.status_code==404: return r
        r.raise_for_status(); return r
    return last if hasattr(last,"status_code") else None

def walk(obj,path="root",out=None):
    if out is None: out=[]
    if isinstance(obj,dict):
        if any(k in obj for k in ("fileName","filePath","url","license","licenseId")):
            out.append((path,obj))
        for k,v in obj.items(): walk(v,path+"."+str(k),out)
    elif isinstance(obj,list):
        for i,v in enumerate(obj): walk(v,path+f"[{i}]",out)
    return out

def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()

batch=[]
for rid,info in targets.items():
    td=OUT/f"m5_{rid:03d}"; td.mkdir(exist_ok=True)
    u=f"https://portal.wiktrop.org/species/show/{info['species_id']}"
    r=get(u)
    if r is None or getattr(r,"status_code",0)!=200:
        rec={"id":rid,"status":"SPECIES_FETCH_FAILED","url":u}
        batch.append(rec); print(json.dumps(rec),flush=True); continue
    (td/"species.html").write_bytes(r.content)
    soup=BeautifulSoup(r.text,"html.parser"); nd=soup.find("script",id="__NEXT_DATA__")
    if not nd:
        rec={"id":rid,"status":"NO_NEXT_DATA","url":u}
        batch.append(rec); print(json.dumps(rec),flush=True); continue
    data=json.loads(nd.string); (td/"next_data.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    hits=walk(data)
    slim=[]; seen=set()
    for path,d in hits:
        fn=d.get("fileName") or d.get("filePath") or d.get("path")
        if not fn or not isinstance(fn,str): continue
        if not re.search(r'\.(jpe?g|png|webp|tif?f)$',fn,re.I): continue
        if fn in seen: continue
        seen.add(fn); slim.append({"path":path,"fileName":fn,"dict":d})
    rows=[]
    for j,x in enumerate(slim,1):
        fn=x["fileName"].lstrip("/")
        candidates=[
          "https://portal.wiktrop.org/files-api/api/get/raw/species/"+fn,
          "https://portal.wiktrop.org/files-api/api/get/raw/speciesResources/"+fn,
          "https://portal.wiktrop.org/files-api/api/get/raw/"+fn,
        ]
        got=None
        for raw in candidates:
            try:
                q=get(raw)
                if q is None or q.status_code!=200: continue
                b=q.content; im=Image.open(io.BytesIO(b)); im.load(); got=(q,b,im); break
            except Exception:
                continue
        if not got: continue
        q,b,im=got; ext="."+((im.format or "JPEG").lower().replace("jpeg","jpg"))
        p=td/f"media_{j:03d}{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        rows.append({"idx":j,"target":info["target"],"species_id":info["species_id"],"json_path":x["path"],"fileName":x["fileName"],
          "raw_url":q.url,"width":im.width,"height":im.height,"bytes":len(b),"format":im.format,
          "sha1":s1,"sha256":s256,"meta":x["dict"],"file":str(p)})
    (td/"manifest.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    thumbs=[]
    for i,row in enumerate(rows,1):
        im=Image.open(row["file"]).convert("RGB"); im.thumbnail((300,220))
        tile=Image.new("RGB",(330,280),"white"); tile.paste(im,((330-im.width)//2,5))
        d=ImageDraw.Draw(tile); d.text((8,230),f"{i}: {row['width']}x{row['height']}\n{row['fileName'][:42]}",fill="black")
        thumbs.append(tile)
    if thumbs:
        cols=4; rn=(len(thumbs)+cols-1)//cols; sh=Image.new("RGB",(cols*330,rn*280),"white")
        for i,t in enumerate(thumbs): sh.paste(t,((i%cols)*330,(i//cols)*280))
        sh.save(td/"contact.jpg",quality=88)
    rec={"id":rid,"status":"OK","downloaded":len(rows)}
    batch.append(rec); print(json.dumps(rec),flush=True)
(OUT/"batch_manifest.json").write_text(json.dumps(batch,ensure_ascii=False,indent=2),encoding="utf-8")
