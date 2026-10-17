import base64, io, hashlib, pathlib, requests, fitz
from PIL import Image
URL="https://www.actabotanica.org/wp-content/uploads/2026/02/Phytochemical-Screening-and-Pharmacognostic-studies-and-Antidiabetic-activity-of-Meshashringi-Gymnema-sylvestre-Retz.-R.Br_.-ex.-Sm.-Leaf-and-Stem-Components.pdf"
OUT=pathlib.Path("evidence/m5_t1_037_crop_probe"); OUT.mkdir(parents=True,exist_ok=True)
r=requests.get(URL,timeout=180); r.raise_for_status(); pb=r.content
doc=fitz.open(stream=pb,filetype="pdf"); p=doc[2]
# full page preview ~900px wide
pix=p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
png=pix.tobytes("png")
im=Image.open(io.BytesIO(png)).convert("RGB")
im.thumbnail((900,1300))
bio=io.BytesIO(); im.save(bio,format="JPEG",quality=62,optimize=True)
preview=bio.getvalue(); (OUT/"page3_preview.jpg").write_bytes(preview)
print("PAGE3_PREVIEW_B64="+base64.b64encode(preview).decode(),flush=True)
print("PAGE3_PREVIEW_SHA256="+hashlib.sha256(preview).hexdigest(),flush=True)
# export embedded images, print tiny previews
for j,img in enumerate(p.get_images(full=True),1):
    xref=img[0]
    try: info=doc.extract_image(xref)
    except Exception: continue
    data=info["image"]; ext=info["ext"]
    fp=OUT/f"img{j:02d}.{ext}"; fp.write_bytes(data)
    try:
        ii=Image.open(io.BytesIO(data)).convert("RGB"); ii.thumbnail((500,500))
        b=io.BytesIO(); ii.save(b,format="JPEG",quality=65,optimize=True)
        small=b.getvalue(); (OUT/f"img{j:02d}_preview.jpg").write_bytes(small)
        print(f"IMG{j}_META={info.get('width')}x{info.get('height')} {ext} sha256={hashlib.sha256(data).hexdigest()}",flush=True)
        print(f"IMG{j}_B64="+base64.b64encode(small).decode(),flush=True)
    except Exception as e:
        print(f"IMG{j}_ERR={e}",flush=True)
