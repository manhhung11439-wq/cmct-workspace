import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_094_pulsatilla"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC5216359"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/9.0 exact Pulsatilla chinensis commercial root figure acquisition"
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
figs=[]
target=None
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    rec={"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs}
    figs.append(rec)
    if "Photos of commercial Baitouweng products" in ct: target=rec
if not target: raise RuntimeError("Figure 3 commercial products not found")
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline images ZIP missing")
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
        if im.width<500 or im.height<300: continue
        ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
        p=OUT/f"figure3_original.{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        orig.append({"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
        break
if not orig: raise RuntimeError("Figure 3 original not extracted")
text=" ".join("".join(root.itertext()).split())
# Persist exact Table 3 evidence around Y1 and Y5 and license text around copyright.
for needle,name in [("Y1","table3_context.txt"),("Creative Commons Attribution 4.0","license_context.txt")]:
    idx=text.find(needle)
    ctx=text[max(0,idx-2000):idx+5000] if idx>=0 else ""
    (OUT/name).write_text(ctx,encoding="utf-8")
man={"id":94,"article":"Shi Y. et al., Scientific Reports 2017;7:40000","doi":"10.1038/srep40000","pmc":PMC,
     "article_license":"CC BY 4.0","figure":target,"original":orig[0],
     "identity_logic":"Table 3 identifies commercial samples Y1 and Y5 as root products with ITS2 BLAST identification Pulsatilla chinensis (Y1 100%; Y5 99.5%) and positive specific PCR/PCR-RFLP authentication.",
     "controller_status":"FIGURE3_ORIGINAL_ACQUIRED; exact Y1/Y5 crop requires visual coordinate lock"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
