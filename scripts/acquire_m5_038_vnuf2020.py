import pathlib,requests,time,hashlib,json,fitz
OUT=pathlib.Path("evidence/m5_t1_038_vnuf2020"); OUT.mkdir(parents=True,exist_ok=True)
URL="https://journal.vnuf.edu.vn/en/article/download/612/530/1057"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/33.0"
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
if not pb.startswith(b"%PDF"): raise RuntimeError("not pdf "+str(r.headers))
pdf=OUT/"article.pdf"; pdf.write_bytes(pb)
doc=fitz.open(stream=pb,filetype="pdf")
page=doc[1]
# page 2 high-res render and embedded images
pix=page.get_pixmap(matrix=fitz.Matrix(4,4),alpha=False); pix.save(OUT/"page2_4x.png")
imgs=[]
for j,img in enumerate(page.get_images(full=True),1):
    xref=img[0]
    try: info=doc.extract_image(xref)
    except Exception: continue
    data=info["image"]; ext=info["ext"]
    p=OUT/f"page2_image_{j}.{ext}"; p.write_bytes(data)
    s1,s256=hh(data)
    imgs.append({"index":j,"xref":xref,"file":str(p),"width":info.get("width"),"height":info.get("height"),"ext":ext,"bytes":len(data),"sha1":s1,"sha256":s256})
text=page.get_text("text")
man={"id":38,"target":"Xạ Đen / Celastrus hindsii Benth.","url":r.url,
     "pdf_bytes":len(pb),"pdf_sha1":hh(pb)[0],"pdf_sha256":hh(pb)[1],"pages":len(doc),
     "page2_text":text,"page2_images":imgs,
     "rights_basis":"JFST open access statement grants read/download/copy/distribute/print full texts without permission; controller will use intact Figure 1 only, no derivative crop.",
     "controller_status":"SOURCE ACQUIRED; FIGURE1 EMBEDDED IMAGE REQUIRES VISUAL LOCK"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
