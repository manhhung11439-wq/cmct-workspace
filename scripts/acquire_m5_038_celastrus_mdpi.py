import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_038_celastrus_mdpi"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC6630900"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/32.2 exact Celastrus hindsii dried-powder figure acquisition"
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
txt=" ".join("".join(root.itertext()).split())
licenses=[{"type":x.attrib.get("license-type",""),"text":" ".join("".join(x.itertext()).split())} for x in root.iter("license")]
figs=[]
for fig in root.iter("fig"):
  lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
  cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
  hrefs=[]
  for g in fig.iter("graphic"):
    h=g.attrib.get(XL) or g.attrib.get("href") or ""
    if h: hrefs.append(h)
  figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
target=next((f for f in figs if f["label"].lower().replace(" ","") in ("figure1","fig.1","fig1")),None)
if not target: raise RuntimeError("Figure 1 missing")
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
      if im.width<250 or im.height<180: continue
      ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
      p=OUT/f"figure1_original.{ext}"; p.write_bytes(b)
      s1,s256=hh(b)
      orig.append({"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
      break
if not orig: raise RuntimeError("Figure 1 original not extracted")
ctx=[]
for needle in ["All samples were sterilized, dried in an oven at 30", "pulverized into a fine powder", "Fractionation of EtOAc extract from powder"]:
  k=txt.find(needle)
  if k>=0: ctx.append(txt[max(0,k-700):k+1400])
man={"id":38,"target":"Xạ Đen / Celastrus hindsii Benth. / dried leaves or powder","pmc":PMC,
     "article":"Comprehensive Fractionation of Antioxidants and GC-MS and ESI-MS Fingerprints of Celastrus hindsii Leaves",
     "doi":"10.3390/medicines6020064","licenses":licenses,"figure":target,"original":orig[0],
     "material_context":ctx,"controller_status":"ORIGINAL_ACQUIRED; visual controller must determine whether Figure 1 contains actual medicinal powder"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
