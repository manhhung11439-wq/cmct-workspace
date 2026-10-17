import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_125_pmc3733203"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC3733203"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/34.0 Scoparia dulcis pharmacognosy figure acquisition"
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
licenses=[{"type":x.attrib.get("license-type",""),"text":" ".join("".join(x.itertext()).split())} for x in root.iter("license")]
figs=[]
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true"); zb=sr.content
(OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inlineImages ZIP missing")
imgs=[]
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist()
    for fi,f in enumerate(figs,1):
        stems=[pathlib.PurePosixPath(h).name.lower().rsplit(".",1)[0] for h in f["graphics"]]
        found=None
        for n in names:
            bn=pathlib.PurePosixPath(n).name.lower()
            if stems and not any(st and st in bn for st in stems): continue
            try:
                b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
            except: continue
            if im.width<150 or im.height<100: continue
            ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
            p=OUT/f"fig_{fi:02d}.{ext}"; p.write_bytes(b)
            s1,s256=hh(b)
            found={"figure_index":fi,"label":f["label"],"caption":f["caption"],"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256}
            imgs.append(found); break
text=" ".join("".join(root.itertext()).split())
ctx=[]
for needle in ["whole plant","dried","shade","powder","macroscopic","morphology"]:
    k=text.lower().find(needle.lower())
    if k>=0: ctx.append(text[max(0,k-800):k+1600])
man={"id":125,"target":"Cam Thảo Đất / Scoparia dulcis L. / whole plant","pmc":PMC,"licenses":licenses,
     "xml_sha1":hh(xb)[0],"xml_sha256":hh(xb)[1],"figures":figs,"images":imgs,"contexts":ctx,
     "controller_status":"FIGURES ACQUIRED; exact material role and reusable license require controller review"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps(man,ensure_ascii=False),flush=True)
