import requests,pathlib,json,hashlib,time
import fitz
OUT=pathlib.Path("evidence/m5_t1_075_indigo"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC11013892"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/17.1 Strobilanthes cusia Indigo Naturalis evidence"
def fetch(u):
    last=None
    for i in range(6):
        try:
            r=s.get(u,timeout=180,allow_redirects=True); last=r
            if r.status_code in (429,500,502,503,504):
                time.sleep(min(30,2*(2**i))); continue
            return r
        except requests.RequestException:
            time.sleep(min(30,2*(2**i)))
    return last
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()

urls=[
 "https://phaidra.vetmeduni.ac.at/api/object/o%3A4359/download",
 "https://phaidra.vetmeduni.ac.at/api/object/o:4359/download",
 "https://phaidra.vetmeduni.ac.at/detail/o%3A4359.pdf",
 "https://mdpi-res.com/d_attachment/plants/plants-13-00918/article_deploy/plants-13-00918.pdf",
 "https://mdpi-res.com/d_attachment/plants/plants-13-00918/article_deploy/plants-13-00918-v2.pdf",
 "https://www.mdpi.com/2223-7747/13/7/918/pdf"
]
attempts=[]; pdfb=None; pdf_url=None
for u in urls:
    r=fetch(u)
    if r is None:
        attempts.append({"url":u,"error":"no_response"}); continue
    ct=r.headers.get("content-type","")
    rec={"url":u,"final_url":r.url,"status":r.status_code,"content_type":ct,"bytes":len(r.content)}
    attempts.append(rec)
    if r.ok and r.content[:4]==b"%PDF":
        pdfb=r.content; pdf_url=r.url; break
if pdfb is None:
    (OUT/"download_attempts.json").write_text(json.dumps(attempts,indent=2),encoding="utf-8")
    raise RuntimeError("No PDF candidate succeeded: "+json.dumps(attempts))
pdf=OUT/"article.pdf"; pdf.write_bytes(pdfb)
doc=fitz.open(stream=pdfb,filetype="pdf")
hits=[]
for i,p in enumerate(doc):
    t=p.get_text("text")
    if "AsB.18" in t and "Strobilanthes" in t:
        hits.append(i)
if not hits: raise RuntimeError("Table 2 page with AsB.18 not found")
page_index=hits[0]; page=doc[page_index]
pix=page.get_pixmap(matrix=fitz.Matrix(3,3),alpha=False)
png=OUT/"table2_page.png"; png.write_bytes(pix.tobytes("png"))
text=page.get_text("text")
man={"id":75,"target":"Thanh Đại / Strobilanthes cusia (Nees) Kuntze / Indigo Naturalis",
"article":"Hartl A.; Polleichtner A.; Novak J. Plants 2024, 13, 918",
"doi":"10.3390/plants13070918","pmc":PMC,"license":"CC BY 4.0",
"download_attempts":attempts,"article_pdf":{"source_url":pdf_url,"file":str(pdf),"bytes":len(pdfb),"sha1":hh(pdfb)[0],"sha256":hh(pdfb)[1],"pages":doc.page_count},
"table2":{"pdf_page_index":page_index,"physical_page":page_index+1,"render":str(png),"render_width":pix.width,"render_height":pix.height,"text":text},
"material_logic":"Table 2: AsB.18 = Strobilanthes cusia, Xin Cun China, extraction ADD. Methods: ADD samples were village indigo from previous harvests, species according to interviewees, traditional extraction; local traditional extraction uses lime during aeration.",
"controller_status":"PAGE_ACQUIRED; VISUAL CROP OF AsB.18 REQUIRED BEFORE PROMOTION"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
