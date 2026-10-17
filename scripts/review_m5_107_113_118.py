import base64,io,requests,fitz
from PIL import Image
def emit(label,im):
    x=im.convert("RGB"); x.thumbnail((700,700))
    b=io.BytesIO(); x.save(b,"JPEG",quality=72,optimize=True)
    print(label+"_B64="+base64.b64encode(b.getvalue()).decode(),flush=True)

# 113 exact Commons file
api="https://commons.wikimedia.org/w/api.php"
q=requests.get(api,params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:Lá cẩm.jpg"},timeout=90).json()
ii=next(iter(q["query"]["pages"].values()))["imageinfo"][0]
r=requests.get(ii["url"],timeout=120); r.raise_for_status()
emit("M113",Image.open(io.BytesIO(r.content)))

# 107 detached candidate
q=requests.get(api,params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:Hibiscus Flower in women's hand.jpg"},timeout=90).json()
ii=next(iter(q["query"]["pages"].values()))["imageinfo"][0]
r=requests.get(ii["url"],timeout=120); r.raise_for_status()
emit("M107",Image.open(io.BytesIO(r.content)))

# 118 publisher PDF page-3 embedded images
u="https://jaims.in/jaims/article/download/4517/7518/13697"
pb=requests.get(u,timeout=120).content
doc=fitz.open(stream=pb,filetype="pdf"); p=doc[2]
for j,img in enumerate(p.get_images(full=True),1):
    try:
      info=doc.extract_image(img[0]); im=Image.open(io.BytesIO(info["image"]))
    except: continue
    if im.width>=200 and im.height>=200:
      emit("M118_IMG"+str(j),im)
