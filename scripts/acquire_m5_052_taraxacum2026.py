import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_052_taraxacum2026"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC13295379"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/33.2 Taraxacum mongolicum figure audit"
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
    figs.append({"label":lab,"caption":ct,"graphics":[h for h in hrefs if h]})
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
images=[]
if zipfile.is_zipfile(io.BytesIO(zb)):
    with zipfile.ZipFile(io.BytesIO(zb)) as z:
        names=z.namelist()
        for fi,f in enumerate(figs,1):
            stems=[pathlib.PurePosixPath(h).name.lower().rsplit(".",1)[0] for h in f["graphics"]]
            for n in names:
                bn=pathlib.PurePosixPath(n).name.lower()
                if stems and not any(st and st in bn for st in stems): continue
                try:
                    b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
                except: continue
                if im.width<180 or im.height<120: continue
                ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
                p=OUT/f"fig_{fi:02d}.{ext}"; p.write_bytes(b)
                s1,s256=hh(b)
                images.append({"figure_index":fi,"label":f["label"],"caption":f["caption"],"archive_member":n,"file":str(p),"width":im.width,"height":im.height,"format":im.format,"bytes":len(b),"sha1":s1,"sha256":s256})
                break
# contact sheet
thumbs=[]
for rec in images:
    im=Image.open(rec["file"]).convert("RGB"); im.thumbnail((420,300))
    canvas=Image.new("RGB",(440,350),"white"); canvas.paste(im,((440-im.width)//2,10))
    d=ImageDraw.Draw(canvas); d.text((10,315),f"{rec['label']} {rec['width']}x{rec['height']}",fill="black")
    thumbs.append(canvas)
if thumbs:
    cols=2; rows=(len(thumbs)+cols-1)//cols
    sheet=Image.new("RGB",(cols*440,rows*350),"white")
    for i,t in enumerate(thumbs): sheet.paste(t,((i%cols)*440,(i//cols)*350))
    sheet.save(OUT/"contact.jpg",quality=90)
lic="CC BY 4.0" if ("creativecommons.org/licenses/by/4.0" in article_text or "Creative Commons Attribution" in article_text) else "UNVERIFIED"
man={"id":52,"target":"Bồ Công Anh / Taraxacum mongolicum Hand.-Mazz.","pmc":PMC,"license":lic,
"xml_sha1":hh(xb)[0],"xml_sha256":hh(xb)[1],"figures":figs,"images":images,
"material_statement":"Article §2.2 states dried whole plant of T. mongolicum consisting of roots, stems, leaves and flowers was purchased/authenticated.",
"controller_status":"FIGURES ACQUIRED; visual audit required for actual medicinal-material image"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"license":lic,"figures":[{"label":f["label"],"caption":f["caption"]} for f in figs],"images":images},ensure_ascii=False),flush=True)
