import pathlib,requests,time,hashlib,json,re,urllib.parse
import fitz
from PIL import Image,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_125_jbpr_full"); OUT.mkdir(parents=True,exist_ok=True)
ARTICLE="https://jbpr.in/index.php/jbpr/article/view/956"
VIEWER="https://jbpr.in/index.php/jbpr/article/view/956/827"
s=requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0 CMCT-image-audit/34.1 exact Scoparia dulcis pharmacognosy acquisition",
                  "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
def get(u,headers=None):
  last=None
  for i in range(8):
    r=s.get(u,timeout=180,allow_redirects=True,headers=headers or {}); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(60,2*(2**i))); continue
    return r
  return last
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
# prime OJS session/cookies
a=get(ARTICLE); (OUT/"article.html").write_bytes(a.content)
v=get(VIEWER,headers={"Referer":ARTICLE}); (OUT/"viewer.html").write_bytes(v.content)
if v.status_code!=200: raise RuntimeError(f"viewer status {v.status_code}")
m=re.search(rb'https?://[^"\']+/article/download/956/827/1758',v.content)
PDFURL=(m.group(0).decode() if m else "https://jbpr.in/index.php/jbpr/article/download/956/827/")
# Try same-session download with referer plus query/cache-busters accepted by OJS.
attempts=[]
r=None
for u in ["https://jbpr.in/index.php/jbpr/article/download/956/827/","https://jbpr.in/index.php/jbpr/article/download/956/827",PDFURL, PDFURL+"?download=1", PDFURL+"?inline=1"]:
  rr=get(u,headers={"Referer":VIEWER,"Accept":"application/pdf,*/*;q=0.9"})
  attempts.append({"url":u,"final":rr.url,"status":rr.status_code,"content_type":rr.headers.get("content-type"),"bytes":len(rr.content)})
  if rr.status_code==200 and (rr.content[:4]==b"%PDF" or "pdf" in (rr.headers.get("content-type") or "").lower()):
    r=rr; break
if r is None:
  raise RuntimeError("PDF unavailable after primed viewer session: "+json.dumps(attempts))
b=r.content; pdf=OUT/"article.pdf"; pdf.write_bytes(b)
doc=fitz.open(stream=b,filetype="pdf"); extracted=[]; pages=[]
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
  pix=p.get_pixmap(matrix=fitz.Matrix(2.2,2.2),alpha=False)
  pix.save(OUT/f"page_{i+1:02d}_preview.png")
# contact sheet of extracted images
thumbs=[]
for rec in extracted[:40]:
  try:
    im=Image.open(rec["file"]).convert("RGB"); im.thumbnail((300,220))
  except: continue
  c=Image.new("RGB",(320,260),"white"); c.paste(im,((320-im.width)//2,8))
  ImageDraw.Draw(c).text((8,235),f"p{rec['page']} img{rec['idx']} {rec['width']}x{rec['height']}",fill="black"); thumbs.append(c)
if thumbs:
  cols=3; rows=(len(thumbs)+cols-1)//cols
  sheet=Image.new("RGB",(cols*320,rows*260),"white")
  for k,c in enumerate(thumbs): sheet.paste(c,((k%cols)*320,(k//cols)*260))
  sheet.save(OUT/"contact.jpg",quality=90)
alltext="\n".join(x["text"] for x in pages)
contexts=[]
for needle in ["Creative Commons","CC BY","Scoparia dulcis","whole plant","powder","dried","macroscopy","morphology"]:
  m=re.search(re.escape(needle),alltext,re.I)
  if m: contexts.append(alltext[max(0,m.start()-800):m.end()+1800])
man={"id":125,"target":"Cam Thảo Đất / Scoparia dulcis L. / whole plant dried",
     "article_url":ARTICLE,"viewer_url":VIEWER,"pdf_url":r.url,"attempts":attempts,
     "pdf_bytes":len(b),"pdf_sha1":hh(b)[0],"pdf_sha256":hh(b)[1],"pdf_pages":len(doc),
     "pages":pages,"images":extracted,"contexts":contexts,
     "controller_status":"PDF/images acquired; visual controller must confirm actual dried whole-plant/powder material"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"attempts":attempts,"pdf_bytes":len(b),"sha1":hh(b)[0],"sha256":hh(b)[1],"pages":len(doc),"images":extracted,"contexts":contexts},ensure_ascii=False),flush=True)
