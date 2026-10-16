import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_015_040_figure_scout"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/6.0 exact medicinal-material figure scout"
XL="{http://www.w3.org/1999/xlink}href"

items=[
 {"id":15,"pmc":"PMC7463858","target_species":"Morus alba","target_terms":["technological processing","figure 1"]},
 {"id":40,"pmc":"PMC9126907","target_species":"Cassia tora","target_terms":["optical image","untreated cassia tora","figure 1"]},
]

def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()

def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()

allm={}
for rec in items:
    rid=rec["id"]; pmc=rec["pmc"]; ro=OUT/f"m5_{rid:03d}"; ro.mkdir(exist_ok=True)
    xr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML")
    xb=xr.content; (ro/"fulltext.xml").write_bytes(xb)
    root=ET.fromstring(xb)
    figs=[]
    for fig in root.iter("fig"):
        lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
        cap=fig.find("caption")
        ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
        hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
        hrefs=[x for x in hrefs if x]
        figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
    target=next((f for f in figs if f["label"].lower().replace(" ","") in ("figure1","fig.1","fig1")),None)
    if target is None: target=figs[0] if figs else None
    if not target: raise RuntimeError(f"{pmc}: no figures")
    sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/supplementaryFiles?inlineImages=true")
    zb=sr.content; (ro/"inline_images.zip").write_bytes(zb)
    if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError(f"{pmc}: inline ZIP unavailable")
    extracted=[]
    with zipfile.ZipFile(io.BytesIO(zb)) as z:
        names=z.namelist()
        stems=[pathlib.PurePosixPath(h).name.lower().rsplit(".",1)[0] for h in target["graphics"]]
        for n in names:
            bn=pathlib.PurePosixPath(n).name.lower()
            if target["graphics"] and not any(st and st in bn for st in stems): continue
            try:
                data=z.read(n); im=Image.open(io.BytesIO(data)); im.load()
            except: continue
            if im.width<200 or im.height<150: continue
            ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
            p=ro/f"figure1_original_{len(extracted)+1}.{ext}"; p.write_bytes(data)
            s1,s256=hh(data)
            extracted.append({"archive_member":n,"file":str(p),"bytes":len(data),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
    if not extracted:
        raise RuntimeError(f"{pmc}: no Figure1 original extracted")
    man={"id":rid,"pmc":pmc,"target_species":rec["target_species"],"xml_url":xr.url,
         "xml_sha1":hh(xb)[0],"xml_sha256":hh(xb)[1],"figure":target,"originals":extracted,
         "license_basis":"article license to be controller-verified from PMC metadata; no promotion from this scout alone"}
    (ro/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
    allm[str(rid)]=man
    print("M5_SCOUT",rid,json.dumps(man,ensure_ascii=False),flush=True)
(OUT/"batch_manifest.json").write_text(json.dumps(allm,ensure_ascii=False,indent=2),encoding="utf-8")
