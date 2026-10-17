import base64,io,requests,fitz
from PIL import Image
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/33.3 visual review"
def emit(label,im):
    x=im.convert("RGB"); x.thumbnail((700,700))
    b=io.BytesIO(); x.save(b,"JPEG",quality=72,optimize=True)
    print(label+"_B64="+base64.b64encode(b.getvalue()).decode(),flush=True)
def fetchimg(u):
    r=s.get(u,timeout=120,allow_redirects=True); r.raise_for_status(); return Image.open(io.BytesIO(r.content))
emit("M113",fetchimg("https://upload.wikimedia.org/wikipedia/commons/0/0b/L%C3%A1_c%E1%BA%A9m.jpg"))
emit("M107",fetchimg("https://upload.wikimedia.org/wikipedia/commons/0/0b/Hibiscus_Flower_in_women%27s_hand.jpg"))
u="https://jaims.in/jaims/article/download/4517/7518/13697"
r=s.get(u,timeout=120); r.raise_for_status(); pb=r.content
doc=fitz.open(stream=pb,filetype="pdf"); p=doc[2]
for j,img in enumerate(p.get_images(full=True),1):
    try:
      info=doc.extract_image(img[0]); im=Image.open(io.BytesIO(info["image"]))
    except: continue
    if im.width>=200 and im.height>=200: emit("M118_IMG"+str(j),im)
