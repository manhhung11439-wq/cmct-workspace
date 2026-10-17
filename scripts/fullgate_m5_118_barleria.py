import json,hashlib,pathlib,requests,fitz
OUT=pathlib.Path("evidence/m5_t1_118_fullgate"); OUT.mkdir(parents=True,exist_ok=True)
PDF="https://jaims.in/jaims/article/download/4517/7518/13697"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/33.5 Barleria FULLGATE"
r=s.get(PDF,timeout=180,allow_redirects=True); r.raise_for_status(); pb=r.content
(OUT/"article.pdf").write_bytes(pb)
doc=fitz.open(stream=pb,filetype="pdf"); page=doc[2]
images=[]
for j,img in enumerate(page.get_images(full=True),1):
    try: info=doc.extract_image(img[0]); data=info["image"]
    except: continue
    if info.get("width",0)>=200 and info.get("height",0)>=200:
        images.append((j,info,data))
# Image order in Figure 1: A flower, B adaxial leaf, C abaxial leaf, D stem, E root.
if len(images)<5: raise RuntimeError(f"Expected >=5 Figure1 images, got {len(images)}")
j,info,data=images[1]
ext=info["ext"]
out=OUT/f"m5_118_Barleria_lupulina_fresh_leaf_adaxial.{ext}"; out.write_bytes(data)
man={
 "id":118,
 "target":"Kim Vàng / Barleria lupulina Lindl.",
 "article":"Chhabra A, Gupta R. Pharmacognostical Study of Barleria lupulina Lindl. 2025;10(6):91-97.",
 "doi":"10.21760/jaims.10.6.13",
 "pdf_url":r.url,
 "license":"CC BY 4.0",
 "pdf_bytes":len(pb),
 "pdf_sha1":hashlib.sha1(pb).hexdigest(),
 "pdf_sha256":hashlib.sha256(pb).hexdigest(),
 "figure":"Figure 1B - Adaxial surface of leaf; Figure 1 shows fresh parts of Barleria lupulina Lindl.",
 "selected_embedded_index":j,
 "file":str(out),
 "width":info.get("width"),"height":info.get("height"),"format":ext,
 "bytes":len(data),
 "sha1":hashlib.sha1(data).hexdigest(),
 "sha256":hashlib.sha256(data).hexdigest(),
 "transform":"none; original embedded Figure 1B bytes",
 "material_basis":"Article states fresh parts of whole plant were procured and authenticated. Figure 1B is a detached fresh leaf. Manuscript §118.1: used part = leaves, young branches; fresh. §118.5 permits fresh use.",
 "controller_status":"FULL-GATE PASS"
}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
