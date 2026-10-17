import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_105_peperomia"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC11637809"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/16.1 exact Peperomia pellucida harvested-material figure acquisition"
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
target=next((f for f in figs if "Botanical characteristics of Peperomia pellucida" in f["caption"]),None)
if not target: raise RuntimeError("Target Figure 1 not found")
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline-image ZIP missing")
orig=None
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist()
    exact=[pathlib.PurePosixPath(h).name.lower() for h in target["graphics"]]
    stems=[x.rsplit(".",1)[0] for x in exact]
    for n in names:
        bn=pathlib.PurePosixPath(n).name.lower()
        if exact and bn not in exact and not any(st and st in bn for st in stems):
            continue
        try:
            b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
        except Exception:
            continue
        if im.width<300 or im.height<200: continue
        ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
        p=OUT/f"figure1_original.{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        orig={"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256}
        break
if not orig: raise RuntimeError("Figure 1 original not extracted")

ctx=[]
for needle in ["harvested in Can Tho City", "collected samples were washed", "dried at room temperature", "dried at 35"]:
    k=article_text.lower().find(needle.lower())
    if k>=0: ctx.append(article_text[max(0,k-1000):k+1800])
lic_ok=any(("creativecommons.org/licenses/by/" in x["text"].lower() or "creative commons attribution" in x["text"].lower()) for x in licenses)
man={
 "id":105,
 "target":"Rau Càng Cua / Peperomia pellucida (L.) Kunth / harvested whole herb",
 "article":"Peperomia pellucida's Ingredients, Antioxidant Properties, and Safe Usage as Food and Herbal Medicine",
 "doi":"10.4014/jmb.2406.06025","pmc":PMC,
 "licenses":licenses,"license_gate":"PASS_CC_BY" if lic_ok else "UNVERIFIED",
 "figure":target,"original":orig,"material_context":ctx,
 "controller_status":"ORIGINAL_ACQUIRED; PANEL C REQUIRES VISUAL LOCK AS DETACHED/HARVESTED MATERIAL"
}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_105_MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
