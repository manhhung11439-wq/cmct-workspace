import base64,io,requests,fitz
from PIL import Image
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/33.4 Barleria visual review"
def emit(label,im):
    x=im.convert("RGB"); x.thumbnail((700,700))
    b=io.BytesIO(); x.save(b,"JPEG",quality=70,optimize=True)
    print(label+"_B64="+base64.b64encode(b.getvalue()).decode(),flush=True)
u="https://jaims.in/jaims/article/download/4517/7518/13697"
r=s.get(u,timeout=120); r.raise_for_status()
doc=fitz.open(stream=r.content,filetype="pdf"); p=doc[2]
for j,img in enumerate(p.get_images(full=True),1):
    try: info=doc.extract_image(img[0]); im=Image.open(io.BytesIO(info["image"]))
    except: continue
    if im.width>=200 and im.height>=200: emit("M118_IMG"+str(j),im)
