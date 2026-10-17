import pathlib,requests,time,hashlib,json,re
import fitz
from PIL import Image,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_125_scoparia_jbpr"); OUT.mkdir(parents=True,exist_ok=True)
ARTICLE="https://www.jbpr.in/index.php/jbpr/article/view/956"
PDFS=[
 "https://www.jbpr.in/index.php/jbpr/article/download/956/827",
 "https://www.jbpr.in/index.php/jbpr/article/view/956/827",
 "https://jbpr.in/index.php/jbpr/article/download/956/827",
]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/31.0 Scoparia dulcis pharmacognosy acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
ar=get(ARTICLE); ab=ar.content; (OUT/"article.html").write_bytes(ab)
pb=None; pdfurl=None; attempts=[]
for u in PDFS:
    try:
        r=get(u); ct=(r.headers.get("content-type") or "").lower()
        attempts.append({"url":u,"final":r.url,"status":r.status_code,"content_type":ct,"bytes":len(r.content)})
        if r.content[:4]==b"%PDF" or "pdf" in ct:
            pb=r.content; pdfurl=r.url; break
    except Exception as e: attempts.append({"url":u,"error":repr(e)})
if pb is None: raise RuntimeError("No PDF: "+json.dumps(attempts))
(OUT/"article.pdf").write_bytes(pb); ps1,ps256=hh(pb)
doc=fitz.open(stream=pb,filetype="pdf")
pages=[]; tiles=[]
for i,p in enumerate(doc):
    txt=p.get_text("text")
    pix=p.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False)
    png=OUT/f"page_{i+1:02d}.png"; pix.save(png)
    im=Image.open(png).convert("RGB"); im.thumbnail((420,590))
    tile=Image.new("RGB",(440,630),"white"); tile.paste(im,((440-im.width)//2,5)); ImageDraw.Draw(tile).text((10,600),f"p{i+1}",fill="black"); tiles.append(tile)
    pages.append({"page":i+1,"text":txt[:5000],"images":len(p.get_images(full=True))})
cols=3; rows=(len(tiles)+cols-1)//cols
sheet=Image.new("RGB",(cols*440,rows*630),"white")
for i,t in enumerate(tiles): sheet.paste(t,((i%cols)*440,(i//cols)*630))
sheet.save(OUT/"contact.jpg",quality=90)
# extract embedded images larger than small icons
imgs=[]
seen=set()
for pi,p in enumerate(doc):
    for j,img in enumerate(p.get_images(full=True),1):
        xref=img[0]
        if xref in seen: continue
        seen.add(xref)
        try:
            info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
        except: continue
        w,h=info.get("width",0),info.get("height",0)
        if w<200 or h<120: continue
        fp=OUT/f"embedded_p{pi+1:02d}_xref{xref}.{ext}"; fp.write_bytes(data)
        s1,s256=hh(data)
        imgs.append({"page":pi+1,"xref":xref,"file":str(fp),"width":w,"height":h,"bytes":len(data),"sha1":s1,"sha256":s256,"ext":ext})
man={"id":125,"target":"Cam Thảo Đất / Scoparia dulcis L.","article_url":ar.url,"article_html_bytes":len(ab),"article_html_sha1":hh(ab)[0],"article_html_sha256":hh(ab)[1],
     "article_license":"CC BY 4.0 per article page","pdf_url":pdfurl,"attempts":attempts,"pdf_bytes":len(pb),"pdf_sha1":ps1,"pdf_sha256":ps256,
     "pdf_pages":len(doc),"pages":pages,"embedded_images":imgs,
     "controller_status":"PDF/figures acquired; actual dried whole-plant image must be visually locked before promotion"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"pdf_url":pdfurl,"pages":len(doc),"embedded":imgs},ensure_ascii=False),flush=True)
