import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_045_pcc_bmc"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC8048166"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/28.0 exact PCC raw-material figure acquisition"
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
    hrefs=[]
    for g in fig.iter("graphic"):
        h=g.attrib.get(XL) or g.attrib.get("href") or ""
        if h: hrefs.append(h)
    figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
target=next((f for f in figs if f["label"].lower().replace(" ","") in ("fig.1","fig1","figure1")),None)
if not target: target=next((f for f in figs if "Illustration for as-prepared Phellodendri Chinensis Cortex-based carbon dots" in f["caption"]),None)
if not target: raise RuntimeError("Target Figure 1 not found")

sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline image ZIP missing")
orig=None
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist()
    wanted=[pathlib.PurePosixPath(h).name.lower() for h in target["graphics"]]
    stems=[w.rsplit(".",1)[0] for w in wanted]
    for n in names:
        bn=pathlib.PurePosixPath(n).name.lower()
        if wanted and bn not in wanted and not any(st and st in bn for st in stems): continue
        try:
            b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
        except: continue
        if im.width<400 or im.height<200: continue
        ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
        p=OUT/f"figure1_original.{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        orig={"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256}
        break
if not orig: raise RuntimeError("Figure 1 original not extracted")

ctx=[]
for needle in ["PCC was purchased from Beijing Qiancao Herbal Pieces Co., Ltd", "Phellodendri Chinensis Cortex", "sole precursor"]:
    k=article_text.find(needle)
    if k>=0: ctx.append(article_text[max(0,k-700):k+1600])
man={"id":45,"target":"Hoàng Bá / Phellodendron chinense C.K.Schneid. / Phellodendri Chinensis Cortex",
"article":"Green Phellodendri Chinensis Cortex-based carbon dots for ameliorating imiquimod-induced psoriasis-like inflammation in mice",
"doi":"10.1186/s12951-021-00847-y","pmc":PMC,"licenses":licenses,
"figure":target,"original":orig,"material_context":ctx,
"controller_status":"ORIGINAL ACQUIRED; RAW PCC REGION MUST BE VISUALLY LOCKED BEFORE CROP/PROMOTION"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
