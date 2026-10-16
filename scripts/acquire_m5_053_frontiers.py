import hashlib, json, pathlib, requests, fitz
from PIL import Image
from io import BytesIO

OUT=pathlib.Path("evidence/m5_053_frontiers"); OUT.mkdir(parents=True,exist_ok=True)
url="https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2021.685575/pdf"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.6 source-figure acquisition"
r=s.get(url,timeout=180); r.raise_for_status()
pdf_bytes=r.content
pdf_path=OUT/"Nie_et_al_2021_Isatis_Frontiers_original.pdf"
pdf_path.write_bytes(pdf_bytes)
manifest={"source_url":url,"source_bytes":len(pdf_bytes),"source_sha1":hashlib.sha1(pdf_bytes).hexdigest(),"source_sha256":hashlib.sha256(pdf_bytes).hexdigest(),"source_content_type":r.headers.get("content-type"),"images":[]}
doc=fitz.open(stream=pdf_bytes,filetype="pdf")
page=doc[1]
for n,img in enumerate(page.get_images(full=True),1):
    xref=img[0]
    meta=doc.extract_image(xref)
    data=meta["image"]
    ext=meta["ext"]
    p=OUT/f"page2_image_{n}_xref{xref}.{ext}"
    p.write_bytes(data)
    try:
        im=Image.open(BytesIO(data)); wh=im.size
    except Exception:
        wh=(None,None)
    rec={"n":n,"xref":xref,"filename":p.name,"ext":ext,"width":wh[0],"height":wh[1],"bytes":len(data),"sha1":hashlib.sha1(data).hexdigest(),"sha256":hashlib.sha256(data).hexdigest()}
    manifest["images"].append(rec)
# render whole source page 2 for reference
pix=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
pix.save(str(OUT/"page2_render.png"))
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(json.dumps(manifest,indent=2))
