import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET,re
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_084_oroxylum_seed"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC5877621"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/14.0 exact Oroxylum indicum seed acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
def save_img(b,path):
    im=Image.open(io.BytesIO(b)); im.load()
    pathlib.Path(path).write_bytes(b)
    s1,s256=hh(b)
    return {"file":str(path),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256}

xr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML")
xb=xr.content; (OUT/"fulltext.xml").write_bytes(xb)
root=ET.fromstring(xb)
article_text=" ".join("".join(root.itertext()).split())
licenses=[{"license_type":lic.attrib.get("license-type",""),"text":" ".join("".join(lic.itertext()).split())} for lic in root.iter("license")]
figs=[]
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
target=next((f for f in figs if "Characteristics of Oroxylum indicum seed" in f["caption"]),None)
if not target: raise RuntimeError("Figure 1 Oroxylum seed target not found")
print("TARGET="+json.dumps(target,ensure_ascii=False),flush=True)

sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
epmc=None
if zipfile.is_zipfile(io.BytesIO(zb)):
    with zipfile.ZipFile(io.BytesIO(zb)) as z:
        names=z.namelist(); stems=[pathlib.PurePosixPath(h).name.lower().rsplit(".",1)[0] for h in target["graphics"]]
        print("ZIP_NAMES="+json.dumps(names,ensure_ascii=False),flush=True)
        for n in names:
            bn=pathlib.PurePosixPath(n).name.lower()
            if stems and not any(st and st in bn for st in stems): continue
            try:
                b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
            except: continue
            if im.width<300 or im.height<200: continue
            ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
            epmc=save_img(b,OUT/f"figure1_europepmc_original.{ext}")
            epmc["archive_member"]=n; epmc["source"]="EuropePMC inlineImages"
            break

assets=[]
urls=[
 "https://mdpi-res.com/d_attachment/ijms/ijms-19-00760/article_deploy/html/images/ijms-19-00760-g001.png",
 "https://pub.mdpi-res.com/ijms/ijms-19-00760/article_deploy/html/images/ijms-19-00760-g001.png",
 "https://www.mdpi.com/ijms/ijms-19-00760/article_deploy/html/images/ijms-19-00760-g001.png",
 "https://mdpi-res.com/d_attachment/ijms/ijms-19-00760/article_deploy/html/images/ijms-19-00760-g001-550.jpg"
]
for u in urls:
    try:
        r=get(u)
        im=Image.open(io.BytesIO(r.content)); im.load()
        if im.width<300 or im.height<200: continue
        ext=(im.format or "PNG").lower().replace("jpeg","jpg")
        rec=save_img(r.content,OUT/f"figure1_mdpi_original.{ext}")
        rec["url"]=r.url; rec["source"]="official MDPI deployed asset"
        assets.append(rec); break
    except Exception as e:
        print("MDPI_FAIL",u,repr(e),flush=True)

needle="OIS (Figure 1A) were bought from a Chinese traditional herb store"
i=article_text.find(needle)
materials=article_text[max(0,i-1000):i+1800] if i>=0 else ""
needle2="The air-dried OIS (30 g)"
j=article_text.find(needle2)
dryctx=article_text[max(0,j-800):j+1600] if j>=0 else ""
best=(assets[0] if assets else epmc)
if not best: raise RuntimeError("No usable Figure 1 original acquired")
man={
"id":84,
"target":"Núc Nác / Oroxylum indicum Vent. / hạt Mộc hồ điệp",
"article":"Zhao P. et al., Int J Mol Sci. 2018;19(3):760",
"doi":"10.3390/ijms19030760","pmc":PMC,
"licenses":licenses,"figure":target,
"europepmc_original":epmc,"mdpi_assets":assets,"selected_original":best,
"material_context":materials,"air_dried_context":dryctx,
"controller_status":"FULL-GATE CANDIDATE: exact O. indicum seed; herb-store source; air-dried seed material; CC BY 4.0. Panel A crop requires visual controller."
}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
