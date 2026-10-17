import json,hashlib,pathlib,time,requests
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw,ImageFont
OUT=pathlib.Path("evidence/m5_t1_wiktrop_scan_083_092"); OUT.mkdir(parents=True,exist_ok=True)
targets={
  83:{
    "target":"Cỏ Cứt Lợn / Ageratum conyzoides L.",
    "pages":[
      "https://portal.wiktrop.org/group/Maraichage-Vegetables/observation/show/193",
      "https://portal.wiktrop.org/group/Malherbologie-Weed_Science/observation/show/194",
      "https://portal.wiktrop.org/observation/show/184",
      "https://portal.wiktrop.org/group/Roadside_Weeds_in_Mauritius/observation/show/4973",
      "https://portal.wiktrop.org/observation/show/14353"
    ]
  },
  92:{
    "target":"Cỏ Mần Trầu / Eleusine indica (L.) Gaertn.",
    "pages":[
      "https://portal.wiktrop.org/group/Riz_-_Rice/observation/show/978",
      "https://portal.wiktrop.org/group/Ananas/observation/show/476694",
      "https://portal.wiktrop.org/group/Bananier/observation/show/5594",
      "https://portal.wiktrop.org/group/Ananas/observation/show/492257"
    ]
  }
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/30.0 WIKTROP exact fresh-use scan"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=120,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(30,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
allrows=[]
for rid,info in targets.items():
    tdir=OUT/f"m5_{rid:03d}"; tdir.mkdir(exist_ok=True)
    rows=[]
    for pi,page in enumerate(info["pages"],1):
        pr=get(page); hb=pr.content
        (tdir/f"obs_{pi:02d}.html").write_bytes(hb)
        soup=BeautifulSoup(pr.text,"html.parser")
        nd=soup.find("script",id="__NEXT_DATA__")
        if not nd: continue
        data=json.loads(nd.string)
        pp=data["props"]["pageProps"]["observation"]
        obs=pp.get("observation",{})
        obs_core=obs.get("observation",{})
        accepted=None
        # find accepted/display name from recommendations if present
        for k,v in pp.items():
            if isinstance(v,dict) and "name" in v and isinstance(v.get("name"),str):
                if "Ageratum" in v["name"] or "Eleusine" in v["name"]: accepted=v["name"]
        resources=obs.get("observationResource",[])
        for ri,entry in enumerate(resources,1):
            res=entry.get("resource",{}); lic=entry.get("license") or {}; user=entry.get("userIbp") or {}
            fn=res.get("fileName") or ""
            if not fn: continue
            raw="https://portal.wiktrop.org/files-api/api/get/raw/observations/"+fn
            raw=raw.replace("/observations//","/observations/")
            try:
                ir=get(raw); b=ir.content
                im=Image.open(__import__("io").BytesIO(b)); im.load()
            except Exception as e:
                continue
            ext="."+((im.format or "JPEG").lower().replace("jpeg","jpg"))
            p=tdir/f"obs{pi:02d}_res{res.get('id','x')}{ext}"; p.write_bytes(b)
            s1,s256=hh(b)
            row={
              "id":rid,"target":info["target"],"observation_page":page,"page_title":soup.title.get_text(" ",strip=True) if soup.title else "",
              "observation_id":obs_core.get("id"),"observation_license_id":obs_core.get("licenseId"),
              "resource_id":res.get("id"),"fileName":fn,"raw_url":ir.url,
              "uploaderId":res.get("uploaderId"),"contributor":res.get("contributor"),"author_name":user.get("name"),
              "license_id":lic.get("id"),"license_name":lic.get("name"),"license_url":lic.get("url"),
              "file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,
              "sha1":s1,"sha256":s256
            }
            rows.append(row); allrows.append(row)
    (tdir/"manifest.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    # contact sheet
    thumbs=[]
    for idx,row in enumerate(rows,1):
        try:
            im=Image.open(row["file"]).convert("RGB"); im.thumbnail((300,220))
        except: continue
        tile=Image.new("RGB",(320,280),"white")
        tile.paste(im,((320-im.width)//2,5))
        d=ImageDraw.Draw(tile)
        lab=f"{idx}: obs{row['observation_id']} res{row['resource_id']}\n{row['license_name']} {row['width']}x{row['height']}"
        d.text((8,230),lab,fill="black")
        thumbs.append(tile)
    if thumbs:
        cols=4; rowsn=(len(thumbs)+cols-1)//cols
        sheet=Image.new("RGB",(cols*320,rowsn*280),"white")
        for i,t in enumerate(thumbs): sheet.paste(t,((i%cols)*320,(i//cols)*280))
        sheet.save(tdir/"contact.jpg",quality=88)
print("TOTAL="+str(len(allrows)),flush=True)
print("ROWS="+json.dumps(allrows,ensure_ascii=False),flush=True)
