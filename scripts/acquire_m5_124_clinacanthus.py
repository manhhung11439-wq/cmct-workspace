import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET,re
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_124_clinacanthus"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC7428249"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/6.1 exact Clinacanthus dried-material figure"
def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
xr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML"); xb=xr.content
(OUT/"fulltext.xml").write_bytes(xb); root=ET.fromstring(xb)
license_text=[]
for tag in ("license","license-p","copyright-statement"):
    for e in root.iter(tag):
        t=" ".join("".join(e.itertext()).split())
        if t and t not in license_text: license_text.append(t)
figs=[]
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]; hrefs=[h for h in hrefs if h]
    figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
target=next((f for f in figs if re.sub(r"[^a-z0-9]","",f["label"].lower()) in ("figure1","fig1")),None) or figs[0]
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true"); zb=sr.content
(OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline ZIP unavailable")
orig=[]
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist(); stems=[pathlib.PurePosixPath(h).stem.lower() for h in target["graphics"]]
    for n in names:
        bn=pathlib.PurePosixPath(n).name.lower()
        if stems and not any(st and st in bn for st in stems): continue
        try:
            data=z.read(n); im=Image.open(io.BytesIO(data)); im.load()
        except: continue
        if im.width<200 or im.height<150: continue
        ext=(im.format or "JPEG").lower().replace("jpeg","jpg"); p=OUT/f"figure1_original_{len(orig)+1}.{ext}"; p.write_bytes(data)
        s1,s256=hh(data)
        orig.append({"member":n,"file":str(p),"bytes":len(data),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
if not orig: raise RuntimeError("Figure 1 image not extracted")
# exact materials text
full=" ".join("".join(root.itertext()).split())
needle="The dried leaves and stems of C. nutans were purchased"
materials=full[full.find(needle):full.find(needle)+700] if needle in full else ""
man={"id":124,"pmc":PMC,"figure":target,"originals":orig,"license_text":license_text,"materials_excerpt":materials,
     "xml_sha1":hh(xb)[0],"xml_sha256":hh(xb)[1]}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_124="+json.dumps(man,ensure_ascii=False),flush=True)
