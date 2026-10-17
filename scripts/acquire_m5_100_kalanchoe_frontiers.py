import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_100_kalanchoe_frontiers"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC10200927"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/32.0 Kalanchoe pinnata detached-leaf figure acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
xr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML"); xb=xr.content
(OUT/"fulltext.xml").write_bytes(xb); root=ET.fromstring(xb)
text=" ".join("".join(root.itertext()).split())
figs=[]
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[]
    for g in fig.iter("graphic"):
        h=g.attrib.get(XL) or g.attrib.get("href") or ""
        if h: hrefs.append(h)
    figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
target=next((f for f in figs if "Plantlet formation after leaf detachment" in f["caption"]),None)
if not target: raise RuntimeError("Figure 2 target not found")
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline-image ZIP missing")
orig=[]
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist()
    stems=[pathlib.PurePosixPath(h).name.lower().rsplit(".",1)[0] for h in target["graphics"]]
    for n in names:
        bn=pathlib.PurePosixPath(n).name.lower()
        if stems and not any(st and st in bn for st in stems): continue
        try:
            b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
        except: continue
        if im.width<400 or im.height<250: continue
        ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
        p=OUT/f"figure2_original.{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        orig.append({"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
        break
if not orig: raise RuntimeError("Figure 2 original not extracted")
licenses=[{"type":x.attrib.get("license-type",""),"text":" ".join("".join(x.itertext()).split())} for x in root.iter("license")]
man={"id":100,"target":"Cây Lá Bỏng / Kalanchoe pinnata (Lam.) Pers. / fresh leaf",
"article":"Jácome-Blásquez F, Kim M. Front Plant Sci. 2023;14:1157619","doi":"10.3389/fpls.2023.1157619","pmc":PMC,
"licenses":licenses,"figure":target,"original":orig[0],
"controller_status":"ORIGINAL_ACQUIRED; PANEL VISUAL LOCK REQUIRED BEFORE ANY M5 PROMOTION"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
