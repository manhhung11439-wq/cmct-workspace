# CMCT T1 M5 #71 Dictamnus dasycarpus root-bark supplementary scout
import io,json,hashlib,pathlib,time,zipfile
import requests,fitz
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_071_dictamnus");OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/3.7 Dictamnus root-bark supplementary scout"
def get(url):
    last=None
    for i in range(8):
        r=s.get(url,timeout=180,allow_redirects=True);last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i)));continue
        r.raise_for_status();return r
    last.raise_for_status()
def hh(data):return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()
urls={
 "article_pdf":"https://www.mdpi.com/1422-0067/25/23/13178/pdf",
 "supp":"https://www.mdpi.com/article/10.3390/ijms252313178/s1"
}
manifest={"id":71,"article":"Park S et al. Int J Mol Sci. 2024;25(23):13178","doi":"10.3390/ijms252313178","license":"CC BY 4.0","downloads":{},"files":[]}
for key,url in urls.items():
    r=get(url); data=r.content; s1,s256=hh(data)
    ct=(r.headers.get("content-type") or "").split(";")[0]
    ext=".bin"
    if data.startswith(b"%PDF"):ext=".pdf"
    elif data[:2]==b"PK":ext=".zip"
    elif data.startswith(b"\x89PNG"):ext=".png"
    elif data[:2]==b"\xff\xd8":ext=".jpg"
    p=OUT/f"{key}{ext}";p.write_bytes(data)
    manifest["downloads"][key]={"url":url,"resolved_url":r.url,"content_type":ct,"file":str(p),"bytes":len(data),"sha1":s1,"sha256":s256}
    if ext==".pdf":
        doc=fitz.open(stream=data,filetype="pdf")
        for i,page in enumerate(doc):
            pix=page.get_pixmap(matrix=fitz.Matrix(2.0,2.0),alpha=False)
            pp=OUT/f"{key}_page_{i+1}.png";pix.save(str(pp))
            manifest["files"].append({"kind":"page_render","page":i+1,"file":str(pp),"bytes":pp.stat().st_size})
            for k,img in enumerate(page.get_images(full=True),1):
                xref=img[0];ex=doc.extract_image(xref);b=ex["image"]
                if len(b)<8000:continue
                try:
                    im=Image.open(io.BytesIO(b));w,h=im.size
                except Exception:continue
                ip=OUT/f"{key}_p{i+1}_xref{xref}_{k}.{ex['ext']}";ip.write_bytes(b);a1,a256=hh(b)
                manifest["files"].append({"kind":"embedded_image","page":i+1,"xref":xref,"file":str(ip),"bytes":len(b),"width":w,"height":h,"sha1":a1,"sha256":a256})
    elif ext==".zip":
        zdir=OUT/f"{key}_unzipped";zdir.mkdir(exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(zdir)
        for q in sorted(zdir.rglob("*")):
            if q.is_file():manifest["files"].append({"kind":"zip_member","file":str(q),"bytes":q.stat().st_size})
(OUT/"scout_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_071_SCOUT="+json.dumps(manifest,ensure_ascii=False),flush=True)
