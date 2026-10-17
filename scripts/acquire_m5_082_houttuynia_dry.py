import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_082_houttuynia_dry"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC8440972"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/29.0 Houttuynia dry herb acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
xr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML")
xb=xr.content; (OUT/"fulltext.xml").write_bytes(xb)
root=ET.fromstring(xb); article_text=" ".join("".join(root.itertext()).split())
licenses=[{"type":x.attrib.get("license-type",""),"text":" ".join("".join(x.itertext()).split())} for x in root.iter("license")]
figs=[]
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
target=next((f for f in figs if "above-ground part of dry stems and leaves of H. cordata" in f["caption"]),None)
if not target: raise RuntimeError("Target Figure 1 not found")
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline image ZIP missing")
orig=[]
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist(); wanted=[pathlib.PurePosixPath(h).name.lower() for h in target["graphics"]]
    for n in names:
        bn=pathlib.PurePosixPath(n).name.lower()
        if wanted and bn not in wanted and not any(pathlib.PurePosixPath(h).stem.lower() in bn for h in target["graphics"]):
            continue
        try:
            b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
        except: continue
        if im.width<400 or im.height<250: continue
        ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
        p=OUT/f"figure1_original.{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        orig.append({"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
        break
if not orig: raise RuntimeError("Figure 1 original not extracted")
man={"id":82,"target":"Diếp Cá / Houttuynia cordata Thunb.","article":"Wu Z. et al., Front Pharmacol. 2021;12:714694","doi":"10.3389/fphar.2021.714694","pmc":PMC,
     "licenses":licenses,"figure":target,"original":orig[0],
     "controller_status":"ORIGINAL_ACQUIRED; PANEL C CROP REQUIRES VISUAL LOCK"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
