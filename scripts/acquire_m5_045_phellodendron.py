import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET,re
import requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_045_phellodendron"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC9793729"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/10.1 Phellodendri Chinensis Cortex figure acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
def save_img(b,prefix):
    try:
        im=Image.open(io.BytesIO(b)); im.load()
    except Exception:
        return None
    if im.width<200 or im.height<120: return None
    ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
    p=OUT/f"{prefix}.{ext}"; p.write_bytes(b)
    s1,s256=hh(b)
    return {"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256}

xr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML")
xb=xr.content; (OUT/"fulltext.xml").write_bytes(xb)
root=ET.fromstring(xb)
article_text=" ".join("".join(root.itertext()).split())
licenses=[]
for lic in root.iter("license"):
    licenses.append({"license_type":lic.attrib.get("license-type",""),"text":" ".join("".join(lic.itertext()).split())})
figs=[]
for fig in root.iter("fig"):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    figs.append({"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
target=next((f for f in figs if f["label"].lower().replace(" ","") in ("figure1","fig.1","fig1")),None)
if not target: raise RuntimeError("Figure 1 not found")
print("TARGET="+json.dumps(target,ensure_ascii=False),flush=True)

sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inline image ZIP missing")
archive_images=[]
orig=None
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist(); print("ZIP_NAMES="+json.dumps(names,ensure_ascii=False),flush=True)
    href_bases=[pathlib.PurePosixPath(h).name.lower() for h in target["graphics"]]
    href_stems=[re.sub(r"\.[a-z0-9]+$","",x) for x in href_bases]
    for idx,n in enumerate(names,1):
        try: b=z.read(n)
        except: continue
        info=save_img(b,f"archive_{idx:03d}")
        if not info: continue
        info["archive_member"]=n
        archive_images.append(info)
        bn=pathlib.PurePosixPath(n).name.lower()
        stem=re.sub(r"\.[a-z0-9]+$","",bn)
        if orig is None and (bn in href_bases or stem in href_stems or any(h and (h in bn or bn in h) for h in href_stems)):
            orig={**info,"source":"EuropePMC inline archive"}

# direct OA asset fallback using exact graphic href from XML
if orig is None:
    for href in target["graphics"]:
        candidates=[href]
        if not re.search(r"\.(?:jpe?g|png|gif|tiff?)$",href,re.I):
            candidates += [href+".jpg",href+".jpeg",href+".png"]
        for name in candidates:
            urls=[
              f"https://pmc.ncbi.nlm.nih.gov/articles/{PMC}/bin/{name}",
              f"https://www.ncbi.nlm.nih.gov/pmc/articles/{PMC}/bin/{name}",
              f"https://europepmc.org/articles/{PMC}/bin/{name}",
            ]
            for u in urls:
                try:
                    rr=get(u); info=save_img(rr.content,"figure1_original")
                    if info:
                        orig={**info,"resolved_url":rr.url,"href":href,"source":"direct OA asset fallback"}; break
                except Exception as e:
                    print("DIRECT_FAIL",u,repr(e),flush=True)
            if orig: break
        if orig: break

# If still unmatched, preserve all archive image metadata and fail only after manifest is written.
needle="derived from the dried bark of Phellodendron chinense"
idx=article_text.find(needle)
context=article_text[max(0,idx-800):idx+1200] if idx>=0 else ""
man={"id":45,"target":"Hoàng Bá / Phellodendron chinense C.K.Schneid. / Phellodendri Chinensis Cortex",
"article":"Li M. et al., Drug Design, Development and Therapy 2022;16:4365-4383",
"doi":"10.2147/DDDT.S385301","pmc":PMC,"licenses":licenses,"figure":target,"original":orig,
"archive_images":archive_images,"material_context":context,
"controller_status":"ORIGINAL_ACQUIRED; PCC VISUAL REGION MUST BE LOCKED BEFORE CROP/PROMOTION" if orig else "DEBUG: Figure 1 not matched; archive images preserved"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
if orig is None: raise RuntimeError("Figure 1 still not matched; inspect preserved archive images")
