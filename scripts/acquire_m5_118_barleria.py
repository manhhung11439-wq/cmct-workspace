import json,hashlib,pathlib,time,requests
import fitz
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_118_barleria"); OUT.mkdir(parents=True,exist_ok=True)
PDF="https://jaims.in/jaims/article/download/4517/7518/13697"
ARTICLE="https://jaims.in/jaims/article/view/4517"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/31.6 Barleria lupulina PDF figure acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
pr=get(PDF); pb=pr.content
if pb[:4]!=b"%PDF": raise RuntimeError("Not PDF: "+pr.url+" "+str(pr.headers.get("content-type")))
(OUT/"article.pdf").write_bytes(pb)
ar=get(ARTICLE); ab=ar.content; (OUT/"article_page.html").write_bytes(ab)
doc=fitz.open(stream=pb,filetype="pdf")
target=None
for i,p in enumerate(doc):
    txt=p.get_text("text")
    if "Figure 1" in txt and "Barleria lupulina" in txt and "Adaxial surface of leaf" in txt:
        target=i; break
if target is None: raise RuntimeError("Figure 1 page not found")
page=doc[target]
pix=page.get_pixmap(matrix=fitz.Matrix(3.5,3.5),alpha=False); pix.save(OUT/f"page_{target+1}_3p5x.png")
imgs=[]
for j,img in enumerate(page.get_images(full=True),1):
    xref=img[0]
    try:
        info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
    except Exception: continue
    p=OUT/f"page{target+1:02d}_img{j:02d}.{ext}"; p.write_bytes(data)
    s1,s256=hh(data)
    imgs.append({"idx":j,"xref":xref,"file":str(p),"ext":ext,"width":info.get("width"),"height":info.get("height"),"bytes":len(data),"sha1":s1,"sha256":s256})
# Contact extracted images.
tiles=[]
for row in imgs:
    try:
        im=ImageOps.exif_transpose(Image.open(row["file"])).convert("RGB")
    except: continue
    if im.width<80 or im.height<80: continue
    im.thumbnail((500,350))
    t=Image.new("RGB",(530,410),"white"); t.paste(im,((530-im.width)//2,5))
    ImageDraw.Draw(t).text((8,365),f"img{row['idx']} {row['width']}x{row['height']} {row['ext']}",fill="black")
    tiles.append(t)
if tiles:
    cols=3; rn=(len(tiles)+cols-1)//cols
    sh=Image.new("RGB",(cols*530,rn*410),"white")
    for i,t in enumerate(tiles): sh.paste(t,((i%cols)*530,(i//cols)*410))
    sh.save(OUT/"contact_extracted.jpg",quality=92)
manifest={"id":118,"target":"Kim Vàng / Barleria lupulina Lindl.",
"article":"Chhabra A, Gupta R. Pharmacognostical Study of Barleria lupulina Lindl. 2025;10(6):91-97.",
"doi":"10.21760/jaims.10.6.13","pdf_url":pr.url,"article_url":ar.url,
"license":"CC BY 4.0","pdf_bytes":len(pb),"pdf_sha1":hh(pb)[0],"pdf_sha256":hh(pb)[1],
"pdf_pages":len(doc),"figure_page_index":target,"figure_page_number":target+1,
"images":imgs,
"material_basis":"Article states fresh whole-plant parts were procured/authenticated; collected plant material was washed and shade-dried. Figure 1 B/C show fresh adaxial/abaxial leaf surfaces. Manuscript §118.5 uses leaves and young shoots fresh.",
"controller_status":"PDF + EMBEDDED IMAGES ACQUIRED; VISUAL LOCK REQUIRED"}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
