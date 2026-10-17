import io, json, hashlib, pathlib, requests, fitz
from PIL import Image
URL="https://www.actabotanica.org/wp-content/uploads/2026/02/Phytochemical-Screening-and-Pharmacognostic-studies-and-Antidiabetic-activity-of-Meshashringi-Gymnema-sylvestre-Retz.-R.Br_.-ex.-Sm.-Leaf-and-Stem-Components.pdf"
OUT=pathlib.Path("evidence/m5_t1_037_fullgate_crop"); OUT.mkdir(parents=True,exist_ok=True)
r=requests.get(URL,timeout=180); r.raise_for_status(); pb=r.content
(OUT/"article.pdf").write_bytes(pb)
doc=fitz.open(stream=pb,filetype="pdf"); p=doc[2]
imgs=[]
for img in p.get_images(full=True):
    xref=img[0]
    try:
        info=doc.extract_image(xref); data=info["image"]
    except: continue
    if info.get("width")==709 and info.get("height")==943 and info.get("ext") in ("jpg","jpeg"):
        imgs.append((info,data))
if not imgs: raise RuntimeError("Figure 1 709x943 JPEG not found")
info,data=imgs[0]
orig=OUT/"figure1_original.jpeg"; orig.write_bytes(data)
im=Image.open(io.BytesIO(data)).convert("RGB")
# Panel A occupies the top-left cell of the 3-column Figure 1 grid.
box=(0,0,245,235)
crop=im.crop(box)
out=OUT/"m5_037_Gymnema_sylvestre_dried_leaf_stem_powder_panelA.png"; crop.save(out,"PNG",optimize=True)
cb=out.read_bytes()
man={
 "id":37,
 "source_pdf_url":URL,
 "source_pdf_sha1":hashlib.sha1(pb).hexdigest(),
 "source_pdf_sha256":hashlib.sha256(pb).hexdigest(),
 "figure1_original_file":str(orig),
 "figure1_original_bytes":len(data),
 "figure1_original_width":im.width,
 "figure1_original_height":im.height,
 "figure1_original_sha1":hashlib.sha1(data).hexdigest(),
 "figure1_original_sha256":hashlib.sha256(data).hexdigest(),
 "crop_file":str(out),
 "crop_box":list(box),
 "crop_width":crop.width,
 "crop_height":crop.height,
 "crop_bytes":len(cb),
 "crop_sha1":hashlib.sha1(cb).hexdigest(),
 "crop_sha256":hashlib.sha256(cb).hexdigest(),
 "transform":"crop only; panel A 'Plant powder sample'; no retouch/recolor/content alteration",
 "license":"CC BY 4.0",
 "material_basis":"Article: collected plant material was shade-dried and powdered; Results: powdered leaf and stem material of Gymnema sylvestre; Figure 1A = Plant powder sample.",
 "controller_status":"FULL-GATE EVIDENCE READY; visual crop check required"
}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
import base64
b=io.BytesIO(); crop.resize((490,470)).save(b,"JPEG",quality=80)
print("CROP_PREVIEW_B64="+base64.b64encode(b.getvalue()).decode(),flush=True)
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
