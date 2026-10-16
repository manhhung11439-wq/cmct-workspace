# CMCT T1 M5 #53 reproducible full-gate crop from Chinese Medicine 2023 Fig 3d
import io,json,hashlib,pathlib,time
import requests,fitz
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_fullgate_053_bmc");OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/3.0 reproducible Isatidis Radix prepared-slices crop"
def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True);last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i)));continue
        r.raise_for_status();return r
    last.raise_for_status()
def hh(data):return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()

pdf_url="https://cmjournal.biomedcentral.com/counter/pdf/10.1186/s13020-023-00777-x"
r=get(pdf_url);pdf=r.content
if not pdf.startswith(b"%PDF"):raise RuntimeError("not PDF")
pp=OUT/"m5_053_article_original.pdf";pp.write_bytes(pdf);ps1,ps256=hh(pdf)
doc=fitz.open(stream=pdf,filetype="pdf")
page_idx=6
txt=doc[page_idx].get_text("text")
if "BBLG" not in txt or "Isatidis Radix" not in txt:
    raise RuntimeError("Fig 3d identity not validated on page 7")
imgs=[]
for img in doc[page_idx].get_images(full=True):
    ex=doc.extract_image(img[0]);data=ex["image"]
    if len(data)<100000:continue
    try:
        im=Image.open(io.BytesIO(data));w,h=im.size
    except Exception:continue
    imgs.append((w*h,len(data),img[0],data,ex["ext"],w,h))
if not imgs:raise RuntimeError("no Fig 3 composite")
_,_,xref,comp,ext,w,h=max(imgs,key=lambda z:(z[0],z[1]))
if (w,h)!=(1866,1875):
    raise RuntimeError(f"unexpected Fig 3 composite dimensions {(w,h)}; refuse fixed crop")
cp=OUT/f"m5_053_fig3_composite_original.{ext}";cp.write_bytes(comp);cs1,cs256=hh(comp)
im=Image.open(io.BytesIO(comp)).convert("RGB")
crop_box=(75,1480,470,1840)
crop=im.crop(crop_box)
dp=OUT/"m5_053_Isatidis_Radix_sliced_root_crop.png";crop.save(dp,format="PNG",optimize=False)
ddata=dp.read_bytes();ds1,ds256=hh(ddata)
rec={
 "id":53,
 "manuscript_taxon":"Isatis tinctoria L.",
 "article_taxon":"Isatis indigotica Fort. (medicinal-source synonym context)",
 "medicinal_material":"Isatidis Radix / Bei-Ban-Lan-Gen (BBLG), root",
 "represented_form":"dried medicinal root cut into slices/segments",
 "article":"Li Y, Yu Q-X, Yau L-F, Huang G-K, Lu J-G, Liu X-X, Jiang Z-H, Wang J-R. Chinese Medicine 2023;18:65",
 "doi":"10.1186/s13020-023-00777-x",
 "license":"CC BY 4.0",
 "license_url":"https://creativecommons.org/licenses/by/4.0/",
 "figure":"Fig. 3d",
 "figure_caption":"Photographs and extracted compound chromatogram (ECC) of reference standards and samples; d Isatidis Radix (BBLG).",
 "source_species_evidence":"Article methods identify BBLG samples as roots of Isatis indigotica Fort.; Isatidis Radix is the dried root in pharmacopoeial/Frontiers medicinal-material context.",
 "resolved_pdf_url":r.url,
 "pdf_file":str(pp),"pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,
 "composite_file":str(cp),"composite_bytes":len(comp),"composite_width":w,"composite_height":h,
 "composite_xref":xref,"composite_sha1":cs1,"composite_sha256":cs256,
 "crop_box":crop_box,"derivative_file":str(dp),"derivative_width":crop.width,"derivative_height":crop.height,
 "derivative_bytes":len(ddata),"derivative_sha1":ds1,"derivative_sha256":ds256,
 "transformation":"crop only from Fig. 3d photograph; excludes chromatogram and unrelated panels; no content addition/removal within the selected drug photograph; lossless PNG derivative",
 "caption_control":"Ảnh 5 – Bản Lam Căn (Isatidis Radix): rễ khô đã cắt lát/đoạn. Nguồn: Li et al., Chinese Medicine 2023, Fig. 3d; CC BY 4.0; ảnh đã crop chỉ phần dược liệu."
}
(OUT/"manifest.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print("FULLGATE_M5_053="+json.dumps(rec,ensure_ascii=False),flush=True)
