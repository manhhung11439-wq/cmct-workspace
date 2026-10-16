import io,json,hashlib,pathlib,time,re,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image,ImageDraw,ImageFont

PMC="PMC10838912"
OUT=pathlib.Path("evidence/m5_t1_005_notopterygium_scout"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/5.0 exact NReR figure scout"

def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()

def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
xmlr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML")
xmlb=xmlr.content; (OUT/"fulltext.xml").write_bytes(xmlb)
root=ET.fromstring(xmlb); XL="{http://www.w3.org/1999/xlink}href"
figs=[]
for fig in root.iter("fig"):
    label=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); caption=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    gs=[]
    for g in fig.iter("graphic"):
        h=g.attrib.get(XL) or g.attrib.get("href") or ""
        if h: gs.append(h)
    figs.append({"id":fig.attrib.get("id",""),"label":label,"caption":caption,"graphics":gs})
print("FIGS="+json.dumps(figs,ensure_ascii=False),flush=True)

zr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zdata=zr.content
if not zipfile.is_zipfile(io.BytesIO(zdata)): raise RuntimeError("inline ZIP missing")
(OUT/"inline_files.zip").write_bytes(zdata)
records=[]
with zipfile.ZipFile(io.BytesIO(zdata)) as z:
    names=z.namelist()
    for f in figs:
        for href in f["graphics"]:
            stem=pathlib.PurePosixPath(href).name.lower()
            matches=[n for n in names if pathlib.PurePosixPath(n).name.lower()==stem]
            if not matches:
                st=re.sub(r"\.(?:jpe?g|png|gif|tiff?)$","",stem)
                matches=[n for n in names if re.sub(r"\.(?:jpe?g|png|gif|tiff?)$","",pathlib.PurePosixPath(n).name.lower())==st]
            for n in matches[:1]:
                b=z.read(n)
                try:
                    im=Image.open(io.BytesIO(b)); im.load()
                except: continue
                ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
                p=OUT/f"{f['label'].replace(' ','_')}_{pathlib.PurePosixPath(n).stem}.{ext}"
                p.write_bytes(b); s1,s256=hh(b)
                rec={"label":f["label"],"caption":f["caption"],"href":n,"file":str(p),"w":im.width,"h":im.height,"bytes":len(b),"sha1":s1,"sha256":s256}
                records.append(rec)

# contact sheet
thumbs=[]
for rec in records:
    im=Image.open(rec["file"]).convert("RGB"); im.thumbnail((900,520))
    thumbs.append((rec,im.copy()))
if thumbs:
    W=920; H=sum(im.height+115 for _,im in thumbs)
    sh=Image.new("RGB",(W,H),"white"); dr=ImageDraw.Draw(sh); y=0
    for rec,im in thumbs:
        dr.text((5,y+5),rec["label"]+" | "+rec["caption"][:130],fill="black")
        y+=75; sh.paste(im,(5,y)); y+=im.height+35
    sh.save(OUT/"figure_contact_sheet.jpg",quality=90)
manifest={"pmcid":PMC,"license":"CC BY 4.0 per article","figures":figs,"assets":records}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("ASSETS="+json.dumps(records,ensure_ascii=False),flush=True)
