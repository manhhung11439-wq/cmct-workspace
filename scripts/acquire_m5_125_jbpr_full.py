import pathlib,requests,time,hashlib,json,re
import fitz
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_125_jbpr_full"); OUT.mkdir(parents=True,exist_ok=True)
URL="https://jbpr.in/index.php/jbpr/article/download/956/827/1758"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/33.0 exact Scoparia dulcis pharmacognosy acquisition"
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=180,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(60,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
r=get(URL); b=r.content
if b[:4]!=b"%PDF": raise RuntimeError(f"Not PDF: {r.status_code} {r.url} {r.headers.get('content-type')} {len(b)}")
pdf=OUT/"article.pdf"; pdf.write_bytes(b)
doc=fitz.open(stream=b,filetype="pdf")
pages=[]; extracted=[]
for i,p in enumerate(doc):
  txt=p.get_text("text")
  imgs=[]
  for j,img in enumerate(p.get_images(full=True),1):
    xref=img[0]
    try:
      info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
    except Exception: continue
    if info.get("width",0)<100 or info.get("height",0)<100: continue
    fn=OUT/f"p{i+1:02d}_img{j:02d}.{ext}"; fn.write_bytes(data)
    s1,s256=hh(data)
    rec={"page":i+1,"idx":j,"file":str(fn),"width":info.get("width"),"height":info.get("height"),"bytes":len(data),"sha1":s1,"sha256":s256}
    imgs.append(rec); extracted.append(rec)
  pages.append({"page":i+1,"text":txt,"images":imgs})
# render pages with Scoparia/figure mentions at 3x
rendered=[]
for rec in pages:
  tl=rec["text"].lower()
  if "scoparia dulcis" in tl or "figure" in tl or "fig." in tl:
    p=doc[rec["page"]-1]; pix=p.get_pixmap(matrix=fitz.Matrix(3,3),alpha=False)
    fn=OUT/f"page_{rec['page']:02d}_3x.png"; pix.save(fn); rendered.append(str(fn))
# contact extracted images
thumbs=[]
for rec in extracted[:30]:
  try:
    im=Image.open(rec["file"]).convert("RGB"); im.thumbnail((300,220))
  except: continue
  c=Image.new("RGB",(320,260),"white"); c.paste(im,((320-im.width)//2,10))
  ImageDraw.Draw(c).text((8,235),f"p{rec['page']} img{rec['idx']} {rec['width']}x{rec['height']}",fill="black"); thumbs.append(c)
if thumbs:
  cols=3; rows=(len(thumbs)+cols-1)//cols
  sheet=Image.new("RGB",(cols*320,rows*260),"white")
  for k,c in enumerate(thumbs): sheet.paste(c,((k%cols)*320,(k//cols)*260))
  sheet.save(OUT/"contact.jpg",quality=90)
alltext="\n".join(x["text"] for x in pages)
licctx=[]
for needle in ["Creative Commons","CC BY","license","Scoparia dulcis","powder","dried","whole plant","whole herb","macroscopic"]:
  for m in re.finditer(re.escape(needle),alltext,re.I):
    licctx.append(alltext[max(0,m.start()-500):m.end()+1200]); break
man={"id":125,"target":"Cam Thảo Đất / Scoparia dulcis L. / whole plant dried","url":URL,"final_url":r.url,
"pdf_bytes":len(b),"pdf_sha1":hh(b)[0],"pdf_sha256":hh(b)[1],"pdf_pages":len(doc),
"pages":pages,"rendered_pages":rendered,"contexts":licctx,
"controller_status":"PDF/images acquired; exact material image + file/article reuse rights require controller lock"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"bytes":len(b),"sha1":hh(b)[0],"sha256":hh(b)[1],"pages":len(doc),"images":extracted,"rendered":rendered,"contexts":licctx},ensure_ascii=False),flush=True)
