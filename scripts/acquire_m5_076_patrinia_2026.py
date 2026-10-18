import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_076_patrinia_2026"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC13414910"; XL="{http://www.w3.org/1999/xlink}href"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/34.0 Patrinia scabiosifolia exact-material scout"
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
licenses=[]
for lic in root.iter("license"):
    licenses.append({"type":lic.attrib.get("license-type",""),"text":" ".join("".join(lic.itertext()).split())})
figs=[]
for i,fig in enumerate(root.iter("fig"),1):
    lab=" ".join("".join(fig.find("label").itertext()).split()) if fig.find("label") is not None else ""
    cap=fig.find("caption"); ct=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
    hrefs=[g.attrib.get(XL) or g.attrib.get("href") or "" for g in fig.iter("graphic")]
    hrefs=[h for h in hrefs if h]
    figs.append({"index":i,"id":fig.attrib.get("id",""),"label":lab,"caption":ct,"graphics":hrefs})
print("FIGS="+json.dumps(figs,ensure_ascii=False),flush=True)
sr=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true")
zb=sr.content; (OUT/"inline_images.zip").write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError("inlineImages not ZIP")
imgs=[]
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist()
    for f in figs:
        stems=[pathlib.PurePosixPath(h).name.lower().rsplit(".",1)[0] for h in f["graphics"]]
        matches=[]
        for n in names:
            bn=pathlib.PurePosixPath(n).name.lower()
            if stems and not any(st and st in bn for st in stems): continue
            try:
                b=z.read(n); im=Image.open(io.BytesIO(b)); im.load()
            except: continue
            if im.width<150 or im.height<100: continue
            ext=(im.format or "JPEG").lower().replace("jpeg","jpg")
            p=OUT/f"fig_{f['index']:02d}_{len(matches)+1:02d}.{ext}"; p.write_bytes(b)
            s1,s256=hh(b)
            rec={"figure_index":f["index"],"label":f["label"],"caption":f["caption"],"archive_member":n,
                 "file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,
                 "sha1":s1,"sha256":s256}
            imgs.append(rec); matches.append(rec)
            if len(matches)>=2: break
# simple contact sheet of first image per figure
thumbs=[]
for rec in imgs:
    if any(x[0]==rec["figure_index"] for x in thumbs): continue
    im=Image.open(rec["file"]).convert("RGB"); im.thumbnail((500,360))
    canvas=Image.new("RGB",(520,420),"white"); canvas.paste(im,((520-im.width)//2,20))
    d=ImageDraw.Draw(canvas); d.text((10,385),f"{rec['label']} {rec['width']}x{rec['height']}",fill="black")
    thumbs.append((rec["figure_index"],canvas))
if thumbs:
    cols=2; rows=(len(thumbs)+1)//2
    sheet=Image.new("RGB",(cols*520,rows*420),"white")
    for k,(_,im) in enumerate(thumbs): sheet.paste(im,((k%cols)*520,(k//cols)*420))
    sheet.save(OUT/"contact.jpg",quality=90)
contexts=[]
for needle in ["dried","whole plant","powder","Patrinia scabiosifolia"]:
    pos=0; out=[]
    low=article_text.lower(); nd=needle.lower()
    while True:
        k=low.find(nd,pos)
        if k<0: break
        out.append(article_text[max(0,k-400):k+1000]); pos=k+len(nd)
        if len(out)>=8: break
    contexts.append({"needle":needle,"matches":out})
man={"id":76,"target":"Bại Tương Thảo / Patrinia scabiosifolia Link / whole plant dried","pmc":PMC,
     "licenses":licenses,"figures":figs,"images":imgs,"contexts":contexts,
     "xml_sha1":hh(xb)[0],"xml_sha256":hh(xb)[1],
     "controller_status":"SCOUT ONLY; promote only if an image directly shows exact Patrinia scabiosifolia harvested/dried whole-herb material."}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"licenses":licenses,"nfig":len(figs),"nimages":len(imgs),"contexts":contexts},ensure_ascii=False),flush=True)
