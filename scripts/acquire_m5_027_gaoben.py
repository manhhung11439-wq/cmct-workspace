import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_027_gaoben"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC9207526"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/23.0 exact Gaoben medicinal-material acquisition"
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
root=ET.fromstring(xb)
article_text=" ".join("".join(root.itertext()).split())
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
target=next((f for f in figs if "Gaoben-related medicinal materials in the market" in f["caption"]),None)
if not target: raise RuntimeError("Target Figure 1 not found")
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline-image ZIP missing")
orig=None
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist()
    wanted=[pathlib.PurePosixPath(h).name.lower() for h in target["graphics"]]
    for n in names:
        bn=pathlib.PurePosixPath(n).name.lower()
        if wanted and bn not in wanted and not any(pathlib.PurePosixPath(w).stem in bn for w in wanted):
            continue
        try:
            b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
        except: continue
        if im.width<400 or im.height<250: continue
        ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
        p=OUT/f"figure1_original.{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        orig={"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256}
        break
if not orig: raise RuntimeError("Figure 1 original not extracted")
for needle in ["Ligustici Rhizoma et Radix", "dried rhizome and root of Ligusticum sinense", "Gaoben-related medicinal materials in the market"]:
    k=article_text.lower().find(needle.lower())
    if k>=0:
        (OUT/"context.txt").write_text(article_text[max(0,k-1200):k+2200],encoding="utf-8")
        break
man={"id":27,"target":"Cảo Bản / Ligusticum sinense Oliv. or Ligusticum jeholense Nakai et Kitag.",
"article":"Wei X-P et al. Front Plant Sci. 2022;13:878263","doi":"10.3389/fpls.2022.878263","pmc":PMC,
"licenses":licenses,"figure":target,"original":orig,
"material_logic":"Article defines Gaoben as dried rhizome and root of L. sinense or L. jeholense; Figure 1 labels market medicinal materials A=L. sinense, B=L. jeholense, C=Conioselinum vaginatum, D=Ligusticum sp.",
"controller_status":"ORIGINAL_ACQUIRED; PANELS A+B MUST BE VISUALLY LOCKED AND C+D EXCLUDED BEFORE PROMOTION"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
