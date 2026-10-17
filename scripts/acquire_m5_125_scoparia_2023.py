import pathlib,re,json,hashlib,time,requests,html as htmlmod,urllib.parse
import fitz
from bs4 import BeautifulSoup
OUT=pathlib.Path("evidence/m5_t1_125_scoparia_2023"); OUT.mkdir(parents=True,exist_ok=True)
ARTICLE="https://www.jbpr.in/index.php/jbpr/article/view/956"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/31.1 Scoparia dulcis pharmacognosy acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
def add(arr,u,base):
    if not u: return
    u=htmlmod.unescape(u)
    u=urllib.parse.urljoin(base,u)
    if u not in arr: arr.append(u)
hr=get(ARTICLE); article_html=hr.text
(OUT/"article.html").write_text(article_html,encoding="utf-8")
soup=BeautifulSoup(article_html,"html.parser")
queue=[]
for a in soup.find_all("a",href=True):
    txt=" ".join(a.stripped_strings).lower(); href=a["href"]
    if "pdf" in txt or "/galley/" in href or "/article/download/" in href or "/article/view/956/827" in href: add(queue,href,hr.url)
add(queue,"https://www.jbpr.in/index.php/jbpr/article/view/956/827",hr.url)
add(queue,"https://www.jbpr.in/index.php/jbpr/article/download/956/827",hr.url)
add(queue,"https://www.jbpr.in/index.php/jbpr/article/download/956/827?download=1",hr.url)
seen=[]; pb=None; pdf_url=None
for qi,u in enumerate(list(queue)):
    try:
        r=get(u); ct=(r.headers.get("content-type") or "").lower()
        rec={"url":u,"final":r.url,"status":r.status_code,"content_type":ct,"bytes":len(r.content)}
        seen.append(rec)
        if r.content[:4]==b"%PDF" or "application/pdf" in ct:
            pb=r.content; pdf_url=r.url; break
        if "html" in ct or r.text.lstrip().startswith("<"):
            fn=OUT/f"viewer_{qi+1}.html"; fn.write_text(r.text,encoding="utf-8")
            txt=r.text
            # decode file= query params and common embedded URLs
            for m in re.findall(r'(?:file|downloadUrl|pdfUrl)\s*[:=]\s*["\']([^"\']+)',txt,re.I):
                add(queue,urllib.parse.unquote(m),r.url)
            for m in re.findall(r'https?[^"\'<> ]+',txt):
                if ".pdf" in m.lower() or "/article/download/" in m.lower(): add(queue,m,r.url)
            soup2=BeautifulSoup(txt,"html.parser")
            for tag in soup2.find_all(["iframe","embed","object","a"]):
                val=tag.get("src") or tag.get("data") or tag.get("href")
                if val and ("download" in val.lower() or "pdf" in val.lower() or "viewer" in val.lower()):
                    add(queue,val,r.url)
            # expand newly found queue
            for nu in queue:
                if all(nu!=z.get("url") for z in seen):
                    pass
    except Exception as e: seen.append({"url":u,"error":repr(e)})
    # append-process newly discovered URLs
    if qi+1==len(queue) and pb is None:
        # python list iterator above fixed, so process tail manually below
        pass
# process any queue additions not seen
for u in queue:
    if pb is not None: break
    if any(x.get("url")==u for x in seen): continue
    try:
        r=get(u); ct=(r.headers.get("content-type") or "").lower()
        seen.append({"url":u,"final":r.url,"status":r.status_code,"content_type":ct,"bytes":len(r.content)})
        if r.content[:4]==b"%PDF" or "application/pdf" in ct:
            pb=r.content; pdf_url=r.url; break
    except Exception as e: seen.append({"url":u,"error":repr(e)})
# always persist discovery before fail
(OUT/"discovery.json").write_text(json.dumps({"queue":queue,"seen":seen},ensure_ascii=False,indent=2),encoding="utf-8")
if pb is None:
    print("DISCOVERY="+json.dumps({"queue":queue,"seen":seen},ensure_ascii=False),flush=True)
    raise RuntimeError("PDF not acquired after viewer discovery")
(OUT/"article.pdf").write_bytes(pb)
ps1,ps256=hh(pb)
doc=fitz.open(stream=pb,filetype="pdf")
pages=[]
for i,p in enumerate(doc):
    txt=p.get_text("text")
    pages.append({"index":i,"number":i+1,"text":txt[:5000],"images":len(p.get_images(full=True))})
    if "Figure 1a-f" in txt or "Figure 1a" in txt or "Morphology" in txt:
        p.get_pixmap(matrix=fitz.Matrix(3,3),alpha=False).save(OUT/f"figure1_page_{i+1}_3x.png")
for i in range(min(5,len(doc))):
    doc[i].get_pixmap(matrix=fitz.Matrix(2.2,2.2),alpha=False).save(OUT/f"page_{i+1}_preview.png")
extracted=[]
for rec in pages:
    if "Figure 1a-f" not in rec["text"] and "Morphology" not in rec["text"]: continue
    p=doc[rec["index"]]
    for j,img in enumerate(p.get_images(full=True),1):
        try: info=doc.extract_image(img[0])
        except: continue
        b=info["image"]; ext=info["ext"]; fp=OUT/f"p{rec['number']}_img{j}.{ext}"; fp.write_bytes(b)
        s1,s256=hh(b); extracted.append({"page":rec["number"],"file":str(fp),"width":info.get("width"),"height":info.get("height"),"bytes":len(b),"sha1":s1,"sha256":s256})
man={"id":125,"target":"Scoparia dulcis L. whole plant","article_url":hr.url,"pdf_url":pdf_url,
"license":"CC BY 4.0 per publisher article page","pdf_attempts":seen,"pdf_bytes":len(pb),"pdf_sha1":ps1,"pdf_sha256":ps256,
"pdf_pages":len(doc),"pages":pages,"extracted_images":extracted,
"controller_rule":"§125.5 = uproot whole plant, wash, sun-dry; promote only if Figure 1 visibly shows harvested/dried whole plant or equivalent crude drug, not in-situ living plant."}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"pdf_url":pdf_url,"pages":len(doc),"extracted":extracted},ensure_ascii=False),flush=True)
