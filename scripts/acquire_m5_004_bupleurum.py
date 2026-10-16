# CMCT T1 M5 #4 Bupleurum chinense exact root figure acquisition via PMC/EuropePMC
import io,json,hashlib,pathlib,time,re,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image,ImageDraw

OUT=pathlib.Path("evidence/m5_t1_004_bupleurum"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.1 exact Bupleurum chinense root figure acquisition"
PMC="PMC5448051"
XML_URL=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML"

def get(url,accept=None):
    last=None
    headers={}
    if accept: headers["Accept"]=accept
    for i in range(8):
        r=s.get(url,headers=headers,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        if r.status_code>=400:
            raise requests.HTTPError(f"{r.status_code} {url}",response=r)
        return r
    last.raise_for_status()

def hh(data): return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()

xr=get(XML_URL,accept="application/xml")
xmlb=xr.content
(OUT/"m5_004_fulltext.xml").write_bytes(xmlb)
xs1,xs256=hh(xmlb)
root=ET.fromstring(xmlb)
ns_xlink="{http://www.w3.org/1999/xlink}href"
figs=[]
for fig in root.iter("fig"):
    label=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    capnode=fig.find("caption")
    caption=" ".join("".join(capnode.itertext()).split()) if capnode is not None else ""
    hrefs=[]
    for g in fig.iter("graphic"):
        href=g.attrib.get(ns_xlink) or g.attrib.get("href") or ""
        if href: hrefs.append(href)
    figs.append({"id":fig.attrib.get("id",""),"label":label,"caption":caption,"graphics":hrefs})
print("M5_004_FIGURES="+json.dumps(figs,ensure_ascii=False),flush=True)

target=None
for f in figs:
    low=(f["label"]+" "+f["caption"]).lower()
    if "roots of bupleurum chinense" in low and "roots of bupleurum scorzonerifolium" in low:
        target=f; break
if target is None: raise RuntimeError("Target Figure 1 not found in fullTextXML")
if not target["graphics"]: raise RuntimeError("Target figure has no graphic href")

downloaded=[]

# Europe PMC officially exposes OA inline images through supplementaryFiles.
try:
    sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
    zdata=sr.content
    (OUT/"m5_004_europepmc_inline_files.zip").write_bytes(zdata)
    if not zipfile.is_zipfile(io.BytesIO(zdata)):
        raise RuntimeError(f"supplementaryFiles did not return ZIP: {sr.headers.get('content-type')}")
    with zipfile.ZipFile(io.BytesIO(zdata)) as z:
        names=z.namelist()
        print("M5_004_INLINE_ZIP_NAMES="+json.dumps(names,ensure_ascii=False),flush=True)
        wanted=set()
        for href in target["graphics"]:
            wanted.add(pathlib.PurePosixPath(href).name.lower())
        matches=[n for n in names if pathlib.PurePosixPath(n).name.lower() in wanted]
        if not matches:
            # tolerate archive path/extension variants, but require the same Figure 1 stem.
            matches=[n for n in names if "bmri2017-7597596.001" in pathlib.PurePosixPath(n).name.lower()]
        for n in matches:
            data=z.read(n)
            try:
                im=Image.open(io.BytesIO(data)); im.load()
            except Exception:
                continue
            if im.width<200 or im.height<200: continue
            ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
            p=OUT/f"m5_004_fig1_original.{ext}"; p.write_bytes(data)
            s1,s256=hh(data)
            downloaded.append({"href":n,"resolved_url":sr.url+"#"+n,"file":str(p),"bytes":len(data),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256,"source":"EuropePMC supplementaryFiles inline image ZIP"})
            break
except Exception as e:
    print("EUROPEPMC_INLINE_FAIL",repr(e),flush=True)

# Fallback direct asset routes only if the official inline-image ZIP did not yield the figure.
if not downloaded:
    for href in target["graphics"]:
        names=[href]
        if not re.search(r"\.(?:jpe?g|png|gif|tiff?)$",href,re.I):
            names += [href+".jpg",href+".jpeg",href+".png"]
        for name in names:
            urls=[
              f"https://pmc.ncbi.nlm.nih.gov/articles/{PMC}/bin/{name}",
              f"https://www.ncbi.nlm.nih.gov/pmc/articles/{PMC}/bin/{name}",
              f"https://europepmc.org/articles/{PMC}/bin/{name}",
            ]
            ok=False
            for u in urls:
                try:
                    rr=get(u)
                    data=rr.content
                    im=Image.open(io.BytesIO(data)); im.load()
                    if im.width<200 or im.height<200: continue
                    ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
                    p=OUT/f"m5_004_fig1_original.{ext}"; p.write_bytes(data)
                    s1,s256=hh(data)
                    downloaded.append({"href":href,"resolved_url":rr.url,"file":str(p),"bytes":len(data),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256,"source":"direct OA asset fallback"})
                    ok=True; break
                except Exception as e:
                    print("FIG_SOURCE_FAIL",u,repr(e),flush=True)
            if ok: break

if not downloaded: raise RuntimeError("Could not download target figure original")
src=downloaded[0]
im=Image.open(src["file"]).convert("RGB")

# Produce a review sheet + four provisional quadrants ONLY for controller inspection.
# No quadrant is automatically promoted; panel C must be visually confirmed first.
w,h=im.size
boxes={"A":(0,0,w//2,h//2),"B":(w//2,0,w,h//2),"C":(0,h//2,w//2,h),"D":(w//2,h//2,w,h)}
derivs={}
for label,box in boxes.items():
    cr=im.crop(box)
    p=OUT/f"m5_004_provisional_panel_{label}.png"; cr.save(p,format="PNG")
    data=p.read_bytes(); s1,s256=hh(data)
    derivs[label]={"file":str(p),"crop_box":box,"width":cr.width,"height":cr.height,"bytes":len(data),"sha1":s1,"sha256":s256,"status":"PROVISIONAL_REVIEW_ONLY"}

thumb=im.copy(); thumb.thumbnail((1200,900))
sheet=Image.new("RGB",(thumb.width,thumb.height+60),"white"); sheet.paste(thumb,(0,60))
dr=ImageDraw.Draw(sheet); dr.text((10,10),"Bupleurum Figure 1 original — verify panel C before promotion",fill="black")
sheet.save(OUT/"m5_004_fig1_review.png")

manifest={
 "id":4,
 "article":"Yang F et al. BioMed Research International 2017;2017:7597596",
 "doi":"10.1155/2017/7597596",
 "pmcid":PMC,
 "license":"CC BY",
 "xml_url":xr.url,"xml_bytes":len(xmlb),"xml_sha1":xs1,"xml_sha256":xs256,
 "target_figure":target,
 "original_figure":src,
 "provisional_quadrants":derivs,
 "controller_note":"Do not promote until exact panel C crop is visually verified; quadrants are review aids only."
}
(OUT/"extract_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_004_ORIGINAL="+json.dumps(src,ensure_ascii=False),flush=True)
print("M5_004_PROVISIONAL="+json.dumps(derivs,ensure_ascii=False),flush=True)
print("M5_004_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
