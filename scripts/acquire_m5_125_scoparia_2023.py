import pathlib,re,json,hashlib,time,requests
import fitz
from bs4 import BeautifulSoup
OUT=pathlib.Path("evidence/m5_t1_125_scoparia_2023"); OUT.mkdir(parents=True,exist_ok=True)
ARTICLE="https://www.jbpr.in/index.php/jbpr/article/view/956"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/31.0 Scoparia dulcis pharmacognosy acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
hr=get(ARTICLE); html=hr.text
(OUT/"article.html").write_text(html,encoding="utf-8")
soup=BeautifulSoup(html,"html.parser")
pdf_links=[]
for a in soup.find_all("a",href=True):
    txt=" ".join(a.stripped_strings).lower()
    href=requests.compat.urljoin(hr.url,a["href"])
    if "pdf" in txt or "/galley/" in href or "/article/download/" in href or href.endswith("/827"):
        if href not in pdf_links: pdf_links.append(href)
# known OJS fallback
pdf_links += [
    "https://www.jbpr.in/index.php/jbpr/article/view/956/827",
    "https://jbpr.in/index.php/jbpr/article/view/956/827",
]
seen=[]; pb=None; pdf_url=None
for u in pdf_links:
    try:
        r=get(u); ct=(r.headers.get("content-type") or "").lower()
        seen.append({"url":u,"final":r.url,"status":r.status_code,"content_type":ct,"bytes":len(r.content)})
        if r.content[:4]==b"%PDF" or "application/pdf" in ct:
            pb=r.content; pdf_url=r.url; break
    except Exception as e:
        seen.append({"url":u,"error":repr(e)})
if pb is None: raise RuntimeError("PDF not acquired: "+json.dumps(seen))
(OUT/"article.pdf").write_bytes(pb)
ps1,ps256=hh(pb)
doc=fitz.open(stream=pb,filetype="pdf")
pages=[]
for i,p in enumerate(doc):
    txt=p.get_text("text")
    pages.append({"index":i,"number":i+1,"text":txt[:5000],"images":len(p.get_images(full=True))})
    if "Figure 1a-f" in txt or "Figure 1a" in txt or "Morphology" in txt:
        pix=p.get_pixmap(matrix=fitz.Matrix(3,3),alpha=False)
        pix.save(OUT/f"figure1_page_{i+1}_3x.png")
# also export pages 1-4 as previews
for i in range(min(5,len(doc))):
    pix=doc[i].get_pixmap(matrix=fitz.Matrix(2.2,2.2),alpha=False)
    pix.save(OUT/f"page_{i+1}_preview.png")
# embedded images from page(s) containing morphology
extracted=[]
for rec in pages:
    txt=rec["text"]
    if "Figure 1a-f" not in txt and "Morphology" not in txt: continue
    p=doc[rec["index"]]
    for j,img in enumerate(p.get_images(full=True),1):
        xref=img[0]
        try: info=doc.extract_image(xref)
        except: continue
        b=info["image"]; ext=info["ext"]
        fp=OUT/f"p{rec['number']}_img{j}.{ext}"; fp.write_bytes(b)
        s1,s256=hh(b)
        extracted.append({"page":rec["number"],"xref":xref,"file":str(fp),"width":info.get("width"),"height":info.get("height"),"bytes":len(b),"sha1":s1,"sha256":s256})
man={"id":125,"target":"Scoparia dulcis L. whole plant","article_url":hr.url,"pdf_url":pdf_url,
     "license":"CC BY 4.0 per publisher article page","pdf_attempts":seen,
     "pdf_bytes":len(pb),"pdf_sha1":ps1,"pdf_sha256":ps256,"pdf_pages":len(doc),
     "pages":pages,"extracted_images":extracted,
     "controller_rule":"§125.5 = uproot whole plant, wash, sun-dry; promote only if Figure 1 visibly shows harvested/dried whole plant or equivalent crude drug, not in-situ living plant."}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"pdf_url":pdf_url,"pages":len(doc),"extracted":extracted,"attempts":seen},ensure_ascii=False),flush=True)
