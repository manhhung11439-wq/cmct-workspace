import pathlib,requests,time,hashlib,json,re,html as htmllib,urllib.parse
import fitz
OUT=pathlib.Path("evidence/m5_t1_125_scoparia_jbpr2023"); OUT.mkdir(parents=True,exist_ok=True)
START="https://www.jbpr.in/index.php/jbpr/article/view/956/827"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/33.2 Scoparia dulcis pharmacognosy acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        return r
    return last
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
attempts=[]; queue=[START]; seen=set(); pb=None; src=None; discovered=[]
for depth in range(5):
    new=[]
    for u in queue:
        if u in seen: continue
        seen.add(u)
        r=get(u); ct=(r.headers.get("content-type") or "").lower()
        attempts.append({"url":u,"status":r.status_code,"final":r.url,"content_type":ct,"bytes":len(r.content)})
        if r.ok and (r.content[:4]==b"%PDF" or "application/pdf" in ct):
            pb=r.content; src=r.url; break
        if r.ok and "text/html" in ct:
            txt=r.text; (OUT/f"viewer_{len(seen)}.html").write_text(txt,encoding="utf-8",errors="ignore")
            raw=[]
            raw += re.findall(r'''(?:src|href|data|value)=["']([^"']+)["']''',txt,re.I)
            raw += re.findall(r'''["']([^"']*(?:\.pdf|/download/|pdfJs|pdfjs|galley)[^"']*)["']''',txt,re.I)
            raw += re.findall(r'''(?:file|url)\s*[:=]\s*["']([^"']+)["']''',txt,re.I)
            for m in raw:
                m=htmllib.unescape(m).replace("\\/","/")
                if not m or m.startswith("javascript:"): continue
                uu=urllib.parse.urljoin(r.url,m)
                discovered.append(uu)
                low=uu.lower()
                if any(k in low for k in ["/download/","galley",".pdf","pdfjs","article/view/956"]):
                    if uu not in seen: new.append(uu)
    if pb is not None: break
    queue=list(dict.fromkeys(new))
base={"id":125,"target":"Cam Thảo Đất / Scoparia dulcis L. / whole plant medicinal material",
      "article":"Sharma A., Singh Saluja M., Jain P. 2023. Pharmacognostical Analysis and In Vitro Antioxidant Activity of Scoparia dulcis L.",
      "doi":"10.32553/jbpr.v12i1.956","license":"CC BY 4.0",
      "attempts":attempts,"discovered":list(dict.fromkeys(discovered))}
if pb is None:
    base["controller_status"]="VIEWER CRAWLED; PDF URL STILL UNRESOLVED"
    (OUT/"manifest.json").write_text(json.dumps(base,ensure_ascii=False,indent=2),encoding="utf-8")
    print("DISCOVERY="+json.dumps(base,ensure_ascii=False),flush=True)
    raise SystemExit(0)
pdf=OUT/"article.pdf"; pdf.write_bytes(pb); s1,s256=hh(pb)
doc=fitz.open(stream=pb,filetype="pdf")
pages=[]; imgs=[]
for i,p in enumerate(doc):
    txt=p.get_text("text")
    pages.append({"page":i+1,"text_head":txt[:2800],"images":len(p.get_images(full=True))})
    pix=p.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False); pix.save(OUT/f"page_{i+1:02d}.png")
    for j,img in enumerate(p.get_images(full=True),1):
        xref=img[0]
        try:
            info=doc.extract_image(xref); data=info["image"]; ext=info["ext"]
        except: continue
        if info.get("width",0)<180 or info.get("height",0)<120: continue
        pth=OUT/f"p{i+1:02d}_img{j:02d}.{ext}"; pth.write_bytes(data)
        h1,h256=hh(data)
        imgs.append({"page":i+1,"xref":xref,"file":str(pth),"width":info.get("width"),"height":info.get("height"),"ext":ext,"bytes":len(data),"sha1":h1,"sha256":h256})
base.update({"source_url":src,"pdf_bytes":len(pb),"pdf_sha1":s1,"pdf_sha256":s256,"pdf_pages":len(doc),
             "pages":pages,"images":imgs,
             "controller_status":"PDF/embedded images acquired; actual medicinal-material image requires visual lock"})
(OUT/"manifest.json").write_text(json.dumps(base,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST_SUMMARY="+json.dumps({"source_url":src,"pdf_pages":len(doc),"images":imgs},ensure_ascii=False),flush=True)
