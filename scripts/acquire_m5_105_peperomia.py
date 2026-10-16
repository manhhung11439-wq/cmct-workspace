import requests,pathlib,json,hashlib,time,fitz
OUT=pathlib.Path("evidence/m5_t1_105_peperomia"); OUT.mkdir(parents=True,exist_ok=True)
url="https://www.jmb.or.kr/journal/download_pdf.php?doi=10.4014%2Fjmb.2406.06025"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.9 Peperomia original journal PDF"
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(30,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
r=get(url); data=r.content
if not data.startswith(b"%PDF"): raise RuntimeError("journal PDF not retrieved")
pdf=OUT/"jmb_2406_06025.pdf"; pdf.write_bytes(data)
s1=hashlib.sha1(data).hexdigest(); s256=hashlib.sha256(data).hexdigest()
doc=fitz.open(pdf)
# article starts at journal p2321; Fig 1 appears on journal p2323 => PDF index 2
page=doc[2]
pix=page.get_pixmap(matrix=fitz.Matrix(2.2,2.2),alpha=False)
png=OUT/"m5_105_fig1_page3_render.png"; pix.save(png)
pb=png.read_bytes()
manifest={"id":105,"doi":"10.4014/jmb.2406.06025","title":"Peperomia pellucida's Ingredients, Antioxidant Properties, and Safe Usage as Food and Herbal Medicine",
 "identity":"Peperomia pellucida (L.) Kunth",
 "caption":"Fig. 1. Botanical characteristics of Peperomia pellucida (L.) Kunth. (A) Wild-type P. pellucida. (B) Leaf shape of the vegetable. (C) The whole body of the vegetable. The trees were harvested in Can Tho City, Viet Nam. The collected samples were washed and damaged parts were removed and dried at room temperature and shade conditions.",
 "license":"CC BY (article open-access statement)","pdf_url":r.url,
 "original_pdf":{"file":str(pdf),"bytes":len(data),"sha1":s1,"sha256":s256,"pages":doc.page_count},
 "page_render":{"file":str(png),"page_index":2,"width":pix.width,"height":pix.height,"bytes":len(pb),
 "sha1":hashlib.sha1(pb).hexdigest(),"sha256":hashlib.sha256(pb).hexdigest()}}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_105_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
