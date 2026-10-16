import requests, pathlib, hashlib, json, time
import fitz
OUT=pathlib.Path("evidence/m5_t1_101_paris2017"); OUT.mkdir(parents=True,exist_ok=True)
url="https://innovareacademics.in/journals/index.php/ajpcr/article/download/20984/13040"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/11.0 Paris polyphylla exact rhizome acquisition"
last=None
for i in range(8):
    r=s.get(url,timeout=180,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
        time.sleep(min(60,2*(2**i))); continue
    r.raise_for_status(); break
b=r.content
pdf=OUT/"mayirnao_bhat_2017_paris_polyphylla.pdf"; pdf.write_bytes(b)
sha1=hashlib.sha1(b).hexdigest(); sha256=hashlib.sha256(b).hexdigest()
doc=fitz.open(stream=b,filetype="pdf")
renders=[]
for pno in range(min(3,len(doc))):
    page=doc[pno]
    pix=page.get_pixmap(matrix=fitz.Matrix(2.4,2.4),alpha=False)
    p=OUT/f"page_{pno+1}.png"; pix.save(p)
    bb=p.read_bytes()
    renders.append({"page":pno+1,"file":str(p),"width":pix.width,"height":pix.height,
                    "sha1":hashlib.sha1(bb).hexdigest(),"sha256":hashlib.sha256(bb).hexdigest()})
text='\n'.join(page.get_text() for page in doc)
man={"id":101,"target":"Thất Diệp Nhất Chi Hoa / Paris polyphylla Sm. / rhizome",
     "article":"Mayirnao HS, Bhat AA. Asian J Pharm Clin Res. 2017;10(11):315-319",
     "doi":"10.22159/ajpcr.2017.v10i11.20984",
     "source_url":r.url,"pdf_file":str(pdf),"pdf_bytes":len(b),"pdf_sha1":sha1,"pdf_sha256":sha256,
     "pages":len(doc),"rendered_pages":renders,
     "license_evidence":"PDF text states © 2017 The Authors; open access under CC BY 4.0.",
     "figure_evidence":"PDF text Figure 1: Paris polyphylla: Habit (a), flower (b) and rhizome (c).",
     "text_excerpt_hits":[x for x in ["CC BY","Fig. 1: Paris polyphylla: Habit (a), flower (b) and rhizome (c)"] if x in text],
     "controller_status":"PDF AND FIGURE PAGE ACQUIRED; PANEL C REQUIRES VISUAL LOCK BEFORE CROP/PROMOTION"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
