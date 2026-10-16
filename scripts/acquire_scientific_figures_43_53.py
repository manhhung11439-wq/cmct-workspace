# CMCT T1 scientific-figure acquisition for M5 #43 and #53
import io, os, re, json, tarfile, hashlib, pathlib, time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_scientific_figures_43_53")
OUT.mkdir(parents=True, exist_ok=True)
s=requests.Session()
s.headers["User-Agent"]="CMCT-image-audit/2.5 scientific figure original acquisition"

def get(url, **kw):
    last=None
    for i in range(8):
        r=s.get(url, timeout=120, allow_redirects=True, **kw)
        last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60, 2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()

def hashes(data):
    return hashlib.sha1(data).hexdigest(), hashlib.sha256(data).hexdigest()

def image_info(data):
    with Image.open(io.BytesIO(data)) as im:
        return im.width, im.height, im.format

manifest=[]

# ---- #53 Frontiers Figure 1 original
article53="https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2021.685575/full"
html53=get(article53).text
soup=BeautifulSoup(html53,"html.parser")
fig53=None
# Find figure whose text/caption mentions FIGURE 1 and dried root
for fig in soup.find_all(["figure","div"]):
    txt=" ".join(fig.stripped_strings)
    if ("FIGURE 1" in txt.upper() or "FIGURE 1" in txt) and ("dried root" in txt.lower() or "Isatis" in txt):
        img=fig.find("img")
        if img and (img.get("src") or img.get("data-src")):
            fig53=(fig,img,txt); break
if not fig53:
    # fallback: inspect all images and nearby text/alt
    for img in soup.find_all("img"):
        alt=(img.get("alt") or "")
        src=img.get("src") or img.get("data-src")
        if src and ("figure 1" in alt.lower() or "dried root" in alt.lower()):
            fig53=(img.parent,img,alt); break
if not fig53:
    # XML fallback
    xml=get("https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2021.685575/xml").text
    xs=BeautifulSoup(xml,"xml")
    f=xs.find("fig", {"id": re.compile("1",re.I)}) or xs.find("fig")
    g=f.find("graphic") if f else None
    href=(g.get("xlink:href") or g.get("href")) if g else None
    if not href: raise RuntimeError("Could not resolve Frontiers Figure 1")
    src53=urljoin(article53,href)
    caption53=" ".join(f.stripped_strings)
else:
    _,img53,caption53=fig53
    src53=urljoin(article53,img53.get("src") or img53.get("data-src"))
# Prefer largest/original variant when URL has resize params
src53=src53.replace("/w/","/").replace("/f/","/")
r53=get(src53)
data53=r53.content
w,h,fmt=image_info(data53)
ext={"JPEG":".jpg","PNG":".png","TIFF":".tif"}.get(fmt,".img")
p53=OUT/("m5_053_frontiers_fig1_original"+ext); p53.write_bytes(data53)
sha1,sha256=hashes(data53)
manifest.append({"id":53,"article":article53,"figure":"Figure 1","source_url":src53,"file":str(p53),
 "bytes":len(data53),"width":w,"height":h,"format":fmt,"sha1":sha1,"sha256":sha256,
 "caption":caption53[:1500],"license":"CC BY","authors":"Nie et al. 2021"})

# ---- #43 PMC OA package, locate Fig 1 asset
pmcid="PMC5031759"
oa=get(f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}").text
m=re.search(r'href="([^"]+\.tar\.gz)"',oa)
if not m: raise RuntimeError("No PMC OA tar.gz link")
tar_url=m.group(1).replace("ftp://","https://")
tar_data=get(tar_url).content
(OUT/"PMC5031759_oa_package.tar.gz").write_bytes(tar_data)
tf=tarfile.open(fileobj=io.BytesIO(tar_data),mode="r:gz")
names=tf.getnames()
nxml_name=next(n for n in names if n.endswith(".nxml"))
nxml=tf.extractfile(nxml_name).read()
xs=BeautifulSoup(nxml,"xml")
fig=None
for f in xs.find_all("fig"):
    label=" ".join((f.find("label").stripped_strings if f.find("label") else []))
    cap=" ".join((f.find("caption").stripped_strings if f.find("caption") else []))
    if ("Fig. 1" in label or label.strip() in ("Fig. 1","Figure 1","Fig 1")) or ("dried root" in cap.lower() and "Scutellaria" in cap):
        fig=f; break
if fig is None: raise RuntimeError("PMC Fig 1 not found")
g=fig.find("graphic")
href=(g.get("xlink:href") or g.get("href")) if g else None
if not href: raise RuntimeError("PMC Fig 1 graphic href missing")
# resolve asset inside tar, allowing extension variants
base_dir=str(pathlib.PurePosixPath(nxml_name).parent)
candidates=[n for n in names if pathlib.PurePosixPath(n).stem==pathlib.PurePosixPath(href).stem]
if not candidates:
    candidates=[n for n in names if href in n]
if not candidates: raise RuntimeError(f"PMC figure asset not found for {href}; names sample={names[:20]}")
asset_name=max(candidates,key=lambda n: tf.getmember(n).size)
data43=tf.extractfile(asset_name).read()
w,h,fmt=image_info(data43)
ext={"JPEG":".jpg","PNG":".png","TIFF":".tif"}.get(fmt,pathlib.Path(asset_name).suffix or ".img")
p43=OUT/("m5_043_pmc5031759_fig1_original"+ext); p43.write_bytes(data43)
sha1,sha256=hashes(data43)
caption43=" ".join(fig.find("caption").stripped_strings) if fig.find("caption") else ""
manifest.append({"id":43,"article":"https://pmc.ncbi.nlm.nih.gov/articles/PMC5031759/","figure":"Figure 1",
 "source_url":tar_url+" :: "+asset_name,"file":str(p43),"bytes":len(data43),"width":w,"height":h,"format":fmt,
 "sha1":sha1,"sha256":sha256,"caption":caption43[:1500],"license":"CC BY 4.0",
 "authors":"Zhao Q, Chen X-Y, Martin C. 2016"})

(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("CMCT_SCI_FIG_MANIFEST="+json.dumps(manifest,ensure_ascii=False))
