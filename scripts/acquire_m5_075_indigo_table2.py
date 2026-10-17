import requests,pathlib,json,hashlib,time,tarfile,io,re
import fitz
OUT=pathlib.Path("evidence/m5_t1_075_indigo"); OUT.mkdir(parents=True,exist_ok=True)
PMC="PMC11013892"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/17.0 Strobilanthes cusia indigo Table2 acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
oa=f"https://pmc.ncbi.nlm.nih.gov/utils/oa/oa.fcgi?id={PMC}"
xb=get(oa).content; (OUT/"oa.xml").write_bytes(xb)
import xml.etree.ElementTree as ET
root=ET.fromstring(xb); tgz=None
for x in root.findall(".//link"):
    if x.attrib.get("format")=="tgz": tgz=x.attrib.get("href"); break
if not tgz: raise RuntimeError("OA tgz not found")
if tgz.startswith("ftp://"): tgz="https://"+tgz[6:]
pkg=get(tgz).content; (OUT/"oa.tar.gz").write_bytes(pkg)
extract=OUT/"oa"; extract.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(pkg),mode="r:gz") as tf: tf.extractall(extract)
pdfs=list(extract.rglob("*.pdf"))
if not pdfs: raise RuntimeError("PDF not found in OA package")
pdf=max(pdfs,key=lambda p:p.stat().st_size)
pdfb=pdf.read_bytes()
doc=fitz.open(pdf)
hits=[]
for i,p in enumerate(doc):
    t=p.get_text("text")
    if "AsB.18" in t and "Strobilanthes" in t:
        hits.append(i)
if not hits: raise RuntimeError("Table 2 page with AsB.18 not found")
page_index=hits[0]
page=doc[page_index]
pix=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False)
png=OUT/"table2_page.png"; png.write_bytes(pix.tobytes("png"))
text=page.get_text("text")
man={"id":75,"target":"Thanh Đại / Strobilanthes cusia (Nees) Kuntze / Indigo Naturalis",
"article":"Hartl A.; Polleichtner A.; Novak J. Plants 2024, 13, 918",
"doi":"10.3390/plants13070918","pmc":PMC,"license":"CC BY 4.0",
"oa_package":{"url":tgz,"bytes":len(pkg),"sha1":hh(pkg)[0],"sha256":hh(pkg)[1]},
"article_pdf":{"file":str(pdf),"bytes":len(pdfb),"sha1":hh(pdfb)[0],"sha256":hh(pdfb)[1],"pages":doc.page_count},
"table2":{"pdf_page_index":page_index,"physical_page":page_index+1,"render":str(png),"render_width":pix.width,"render_height":pix.height,"text":text},
"material_logic":"Table 2 sample AsB.18 = Strobilanthes cusia, provenance Xin Cun China, extraction ADD. Article methods state ADD samples were locally available village indigo from previous harvests, species according to interviewees, traditional extraction method; traditional local extraction uses lime during aeration.",
"controller_status":"PAGE_ACQUIRED; VISUAL CROP OF AsB.18 REQUIRED BEFORE PROMOTION"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
