import json,hashlib,pathlib,time,requests,html,re,urllib.parse
from bs4 import BeautifulSoup
import fitz
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_037_gymnema_powder"); OUT.mkdir(parents=True,exist_ok=True)
URL="https://www.actabotanica.org/phytochemical-screening-and-pharmacognostic-studies-and-antidiabetic-activity-of-meshashringi-gymnema-sylvestre-retz-r-br-ex-sm-leaf-and-stem-components/"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/32.2 Gymnema exact dried powder PDF acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
hr=get(URL); hb=hr.content; (OUT/"article.html").write_bytes(hb)
soup=BeautifulSoup(hr.text,"html.parser")
pdf_url=None
for a in soup.find_all("a",href=True):
    h=urllib.parse.urljoin(hr.url,a["href"])
    if h.lower().endswith(".pdf") and "phytochemical" in h.lower():
        pdf_url=h; break
if not pdf_url: raise RuntimeError("Publisher PDF link not found")
pr=get(pdf_url); pb=pr.content
if pb[:4]!=b"%PDF": raise RuntimeError("Publisher PDF URL did not return PDF")
(OUT/"article.pdf").write_bytes(pb); ps1,ps256=hh(pb)
doc=fitz.open(stream=pb,filetype="pdf")
target_page=None
pages=[]
for i,p in enumerate(doc):
    txt=p.get_text("text")
    pages.append({"number":i+1,"text_head":txt[:4500],"images":len(p.get_images(full=True))})
    if "Plant powder sample" in txt or "Morphology of dried plant material" in txt:
        target_page=i
if target_page is None: raise RuntimeError("Figure 1 page not found")
p=doc[target_page]
p.get_pixmap(matrix=fitz.Matrix(3.2,3.2),alpha=False).save(OUT/f"figure1_page_{target_page+1}_3p2x.png")
imgs=[]
for j,img in enumerate(p.get_images(full=True),1):
    xref=img[0]
    try: info=doc.extract_image(xref)
    except: continue
    data=info["image"]; ext=info["ext"]
    fp=OUT/f"p{target_page+1:02d}_img{j:02d}.{ext}"; fp.write_bytes(data)
    s1,s256=hh(data)
    imgs.append({"idx":j,"xref":xref,"file":str(fp),"width":info.get("width"),"height":info.get("height"),"bytes":len(data),"ext":ext,"sha1":s1,"sha256":s256})
text=" ".join(soup.stripped_strings)
ctx=[]
for needle in ["shade-dried", "Morphology of dried plant material", "Plant powder sample", "Creative Commons Attribution"]:
    k=text.lower().find(needle.lower())
    if k>=0: ctx.append(text[max(0,k-900):k+1700])
man={"id":37,"target":"Dây Thìa Canh / Gymnema sylvestre (Retz.) R.Br. ex Schult.",
"article_url":hr.url,"publisher_pdf_url":pr.url,
"article_sha1":hh(hb)[0],"article_sha256":hh(hb)[1],
"pdf_bytes":len(pb),"pdf_sha1":ps1,"pdf_sha256":ps256,"pdf_pages":len(doc),
"license":"CC BY 4.0 per article copyright notice",
"figure_page_number":target_page+1,"images":imgs,"contexts":ctx,
"controller_rule":"Promote only Figure 1A plant powder sample if visually identifiable; article directly defines it as dried powdered leaf+stem material."}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"pdf_url":pr.url,"pdf_sha256":ps256,"page":target_page+1,"images":imgs,"contexts":ctx},ensure_ascii=False),flush=True)
