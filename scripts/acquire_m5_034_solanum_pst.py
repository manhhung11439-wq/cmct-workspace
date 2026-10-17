import pathlib,requests,time,hashlib,json,re,html as htmllib,urllib.parse
import fitz
OUT=pathlib.Path("evidence/m5_t1_034_solanum_pst"); OUT.mkdir(parents=True,exist_ok=True)
URLS=[
 "https://horizonepublishing.com/journals/index.php/PST/article/download/1370/988",
 "https://horizonepublishing.com/journals/index.php/PST/article/view/1370/988"
]
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/32.0 Solanum procumbens PST acquisition"
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=180,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(60,2*(2**i))); continue
    return r
  return last
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
pb=None; src=None; attempts=[]; queue=list(URLS); seen=set()
for depth in range(3):
  new=[]
  for u in queue:
    if u in seen: continue
    seen.add(u); r=get(u); ct=(r.headers.get("content-type") or "").lower()
    attempts.append({"url":u,"status":r.status_code,"final":r.url,"content_type":ct,"bytes":len(r.content)})
    if r.ok and (r.content[:4]==b"%PDF" or "application/pdf" in ct):
      pb=r.content; src=r.url; break
    if r.ok and "text/html" in ct:
      txt=r.text
      for m in re.findall(r'''(?:src|href|data)=["']([^"']+)["']''',txt,re.I):
        uu=urllib.parse.urljoin(r.url,htmllib.unescape(m))
        if any(k in uu.lower() for k in ["download","pdf","1370"]) and uu not in seen: new.append(uu)
  if pb is not None: break
  queue=list(dict.fromkeys(new))
if pb is None: raise RuntimeError("PDF unavailable "+json.dumps(attempts))
(OUT/"article.pdf").write_bytes(pb); ps1,ps256=hh(pb)
doc=fitz.open(stream=pb,filetype="pdf")
pages=[]; imgs=[]
for i,p in enumerate(doc):
  txt=p.get_text("text")
  pages.append({"page":i+1,"text_head":txt[:3500],"images":len(p.get_images(full=True))})
  pix=p.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False); pix.save(OUT/f"page_{i+1:02d}.png")
  for j,img in enumerate(p.get_images(full=True),1):
    xref=img[0]
    try: info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
    except: continue
    if info.get("width",0)<140 or info.get("height",0)<100: continue
    fn=OUT/f"p{i+1:02d}_img{j:02d}.{ext}"; fn.write_bytes(data)
    h1,h256=hh(data)
    imgs.append({"page":i+1,"file":str(fn),"width":info.get("width"),"height":info.get("height"),"ext":ext,"bytes":len(data),"sha1":h1,"sha256":h256})
man={"id":34,"target":"Cà Gai Leo / Solanum procumbens Lour.","article":"Minh NP. Thermal treatments affected to quality attributes of Solanum procumbens Lour. Plant Science Today 2022;9(1):150-156","doi":"10.14719/pst.1370","license":"CC BY 4.0","source_url":src,"attempts":attempts,"pdf_sha1":ps1,"pdf_sha256":ps256,"pages":pages,"images":imgs,"controller_status":"Acquired; actual processed material image requires visual lock"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"source":src,"pages":len(doc),"images":imgs},ensure_ascii=False),flush=True)
