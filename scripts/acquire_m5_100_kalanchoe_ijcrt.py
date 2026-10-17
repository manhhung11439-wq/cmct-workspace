import pathlib,requests,time,hashlib,json
import fitz
OUT=pathlib.Path("evidence/m5_t1_100_kalanchoe_ijcrt"); OUT.mkdir(parents=True,exist_ok=True)
URL="https://ijcrt.org/papers/IJCRT2401126.pdf"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/35.0 Kalanchoe dried-leaf pharmacognosy acquisition"
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=180,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(60,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
r=get(URL); pb=r.content
if pb[:4]!=b"%PDF": raise RuntimeError("not PDF")
(OUT/"article.pdf").write_bytes(pb); ps1,ps256=hh(pb)
doc=fitz.open(stream=pb,filetype="pdf")
imgs=[]; pages=[]
for i,p in enumerate(doc):
  txt=p.get_text("text")
  pages.append({"page":i+1,"text_head":txt[:3500],"images":len(p.get_images(full=True))})
  if i<8:
    pix=p.get_pixmap(matrix=fitz.Matrix(1.7,1.7),alpha=False); pix.save(OUT/f"page_{i+1:02d}.png")
  for j,img in enumerate(p.get_images(full=True),1):
    xref=img[0]
    try:
      info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
    except: continue
    if info.get("width",0)<160 or info.get("height",0)<100: continue
    pth=OUT/f"p{i+1:02d}_img{j:02d}.{ext}"; pth.write_bytes(data)
    h1,h256=hh(data)
    imgs.append({"page":i+1,"xref":xref,"file":str(pth),"width":info.get("width"),"height":info.get("height"),"ext":ext,"bytes":len(data),"sha1":h1,"sha256":h256})
man={"id":100,"target":"Cây Lá Bỏng / Kalanchoe pinnata / dried leaf material","article":"Patidar A., Alawa P. 2024. Evaluation of Anti-diarrheal activity of Dried leaves of Kalanchoe Pinnata Lam.","source_url":r.url,"license":"CC BY 4.0","pdf_bytes":len(pb),"pdf_sha1":ps1,"pdf_sha256":ps256,"pages":pages,"images":imgs,"controller_status":"PDF/images acquired; actual dried-leaf image requires visual lock"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"pages":len(doc),"images":imgs},ensure_ascii=False),flush=True)
