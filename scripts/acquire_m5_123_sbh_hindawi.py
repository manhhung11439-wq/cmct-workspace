import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_123_sbh_hindawi"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC6280310"; DOI="10.1155/2018/4365739"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/32.0 exact Scutellaria barbata dried-herb Figure1 acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
# XML
xr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML"); xb=xr.content
(OUT/"fulltext.xml").write_bytes(xb); root=ET.fromstring(xb)
txt=" ".join("".join(root.itertext()).split())
licenses=[{"type":x.attrib.get("license-type",""),"text":" ".join("".join(x.itertext()).split())} for x in root.iter("license")]
figs=[]
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    figs.append({"label":lab,"caption":ct,"graphics":hrefs})
target=next((f for f in figs if f["label"].lower().replace(" ","") in ("figure1","fig.1","fig1")),None)
if not target: raise RuntimeError("Figure1 not found")
# inline original
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true"); zb=sr.content
(OUT/"inline_images.zip").write_bytes(zb)
orig=[]
if zipfile.is_zipfile(io.BytesIO(zb)):
    with zipfile.ZipFile(io.BytesIO(zb)) as z:
        names=z.namelist(); stems=[pathlib.PurePosixPath(h).name.lower().rsplit(".",1)[0] for h in target["graphics"]]
        for n in names:
            bn=pathlib.PurePosixPath(n).name.lower()
            if stems and not any(st and st in bn for st in stems): continue
            try:
                b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
            except: continue
            if im.width<300 or im.height<200: continue
            ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
            p=OUT/f"figure1_original.{ext}"; p.write_bytes(b)
            s1,s256=hh(b)
            orig.append({"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
            break
# PDF source
pr=get("https://downloads.hindawi.com/journals/ecam/2018/4365739.pdf"); pb=pr.content
(OUT/"article.pdf").write_bytes(pb)
ps1,ps256=hh(pb)
# material context
contexts=[]
for needle in ["dried entire plant of Scutellaria Barbata", "Scutellariae Barbatae Herba", "dried entire plant"]:
    k=txt.lower().find(needle.lower())
    if k>=0: contexts.append(txt[max(0,k-700):k+1200])
man={"id":123,"target":"Bán Chi Liên / Scutellaria barbata D.Don / dried whole herb",
"article":"Gong B. et al. Systematic Investigation of Scutellariae Barbatae Herba for Treating Hepatocellular Carcinoma Based on Network Pharmacology",
"doi":DOI,"pmc":PMC,"licenses":licenses,"figure":target,"original":orig[0] if orig else None,
"pdf_url":pr.url,"pdf_bytes":len(pb),"pdf_sha1":ps1,"pdf_sha256":ps256,
"material_context":contexts,
"controller_status":"ORIGINAL_ACQUIRED; FIGURE1 HERB PHOTO REQUIRES VISUAL CROP LOCK"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
