import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_033_cortex_moutan"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC6152737"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/13.0 Cortex Moutan exact crude-drug figure acquisition"
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
article_text=" ".join("".join(root.itertext()).split())
figs=[]
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
target=next((f for f in figs if "crude drug of guadanpi" in f["caption"].lower()),None)
if not target: raise RuntimeError("Target Figure 1 not found")
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true"); zb=sr.content
(OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline images ZIP missing")
orig=[]
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist()
    wanted={pathlib.PurePosixPath(h).name.lower() for h in target["graphics"]}
    wanted_stems={pathlib.PurePosixPath(h).stem.lower() for h in target["graphics"]}
    for n in names:
        bn=pathlib.PurePosixPath(n).name.lower()
        stem=pathlib.PurePosixPath(n).stem.lower()
        if bn not in wanted and stem not in wanted_stems: continue
        try:
            b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
        except: continue
        if im.width<300 or im.height<200: continue
        ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
        p=OUT/f"figure1_original.{ext}"; p.write_bytes(b)
        s1,s256=hh(b)
        orig.append({"archive_member":n,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
        break
if not orig: raise RuntimeError(f"Figure 1 original missing; target={target}; names={names[:30]}")
lic="CC BY 4.0" if ("creativecommons.org/licenses/by/4.0" in article_text or "Creative Commons Attribution" in article_text) else "UNVERIFIED"
needle="In general, the root of P. suffruticosa"
idx=article_text.find(needle)
context=article_text[max(0,idx-500):idx+1700] if idx>=0 else ""
man={"id":33,"target":"Đan Bì / Paeonia suffruticosa Andrews / Cortex Moutan root bark",
"article":"Wang Z et al. Molecules 2017;22:946","doi":"10.3390/molecules22060946","pmc":PMC,
"article_license":lic,"figure":target,"original":orig[0],"processing_context":context,
"controller_status":"ORIGINAL ACQUIRED; PANEL B/C REQUIRE VISUAL LOCK AND CONTROLLED CROP"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
