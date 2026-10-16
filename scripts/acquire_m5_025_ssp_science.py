import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_025_ssp_science"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC6571576"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/8.1 exact SSP medicinal figure acquisition"
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
target=None
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    if "morphology of soybean" in ct.lower() and "S8 (F)" in ct:
        target={"label":lab,"caption":ct,"graphics":hrefs}; break
if not target: raise RuntimeError("Figure 1 morphology target not found")
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inlineImages ZIP missing")
matches=[]
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist()
    stems=[pathlib.PurePosixPath(h).name.lower().rsplit(".",1)[0] for h in target["graphics"]]
    for n in names:
        bn=pathlib.PurePosixPath(n).name.lower()
        if not any(st and st in bn for st in stems): continue
        try:
            b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
        except: continue
        if im.width<300 or im.height<200: continue
        ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
        p=OUT/f"figure1_original.{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        matches.append({"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
        break
if not matches: raise RuntimeError("Figure 1 original not extracted")
text=" ".join("".join(root.itertext()).split())
lic_ok="Creative Commons Attribution (CC BY) license" in text and "creativecommons.org/licenses/by/4.0" in text
man={"id":25,"article":"Chen et al., Molecules 2019, 24, 1864","doi":"10.3390/molecules24101864","pmc":PMC,
     "article_license":"CC BY 4.0" if lic_ok else "UNVERIFIED","figure":target,"original":matches[0],
     "material_logic":"Paper identifies SSP/dandouchi as fermented preparation from ripe Glycine max seeds. Results state S8 morphology met 2015 China Pharmacopoeia yellow-cladding requirements. Figure 1 panel F = S8.",
     "controller_status":"ORIGINAL_ACQUIRED; PANEL F CROP REQUIRES VISUAL LOCK"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
