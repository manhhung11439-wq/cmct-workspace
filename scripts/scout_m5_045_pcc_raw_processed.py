import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET,re
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_045_pcc_raw_processed"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC10423935"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/10.2 PCC raw processed figure scout"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
def save_img(b,prefix):
    try:
        im=Image.open(io.BytesIO(b)); im.load()
    except: return None
    if im.width<200 or im.height<120: return None
    ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
    p=OUT/f"{prefix}.{ext}"; p.write_bytes(b)
    s1,s256=hh(b)
    return {"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256}

xr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML")
xb=xr.content; (OUT/"fulltext.xml").write_bytes(xb); root=ET.fromstring(xb)
text=" ".join("".join(root.itertext()).split())
licenses=[{"license_type":lic.attrib.get("license-type",""),"text":" ".join("".join(lic.itertext()).split())} for lic in root.iter("license")]
figs=[]
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
print("FIGURES="+json.dumps(figs,ensure_ascii=False),flush=True)
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline image ZIP missing")
imgs=[]
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist(); print("ZIP_NAMES="+json.dumps(names,ensure_ascii=False),flush=True)
    for idx,n in enumerate(names,1):
        try:b=z.read(n)
        except: continue
        info=save_img(b,f"archive_{idx:03d}")
        if info: imgs.append({**info,"archive_member":n})
# attach likely image to each fig by stem matching
for f in figs:
    bases=[pathlib.PurePosixPath(h).name.lower() for h in f["graphics"]]
    stems=[re.sub(r"\.[a-z0-9]+$","",b) for b in bases]
    f["matched_images"]=[x for x in imgs if any(st and st in pathlib.PurePosixPath(x["archive_member"]).name.lower() for st in stems)]
ctx=[]
for needle in ["raw Phellodendri Chinensis Cortex","processed Phellodendri Chinensis Cortex","Phellodendron chinense","dried bark"]:
    idx=text.lower().find(needle.lower())
    if idx>=0: ctx.append(text[max(0,idx-600):idx+1400])
man={"id":45,"target":"Hoàng Bá / Phellodendron chinense / Phellodendri Chinensis Cortex","pmc":PMC,
"article":"Wang et al. Evaluation of raw and processed Phellodendri Chinensis Cortex using the quality marker analysis strategy",
"license":licenses,"figures":figs,"archive_images":imgs,"material_context":ctx,
"controller_status":"SCOUT_ONLY; promote only if a figure/caption directly locks raw or processed PCC material."}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
