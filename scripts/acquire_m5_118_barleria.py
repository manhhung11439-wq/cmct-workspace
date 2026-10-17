import json,hashlib,pathlib,time,requests,urllib.parse,re
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_118_barleria"); OUT.mkdir(parents=True,exist_ok=True)
HTML="https://jaims.in/jaims/article/download/4517/7519?inline=1"
ARTICLE="https://jaims.in/jaims/article/view/4517"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/31.5 Barleria lupulina fresh-parts acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
hr=get(HTML); hb=hr.content; (OUT/"article_inline.html").write_bytes(hb)
ar=get(ARTICLE); ab=ar.content; (OUT/"article_page.html").write_bytes(ab)
soup=BeautifulSoup(hr.text,"html.parser")
wanted={"jaims_4517_02.JPG":"Adaxial surface of leaf","jaims_4517_03.JPG":"Abaxial surface of leaf","jaims_4517_04.JPG":"Stem"}
rows=[]
for img in soup.find_all("img",src=True):
    src=img["src"]
    bn=pathlib.PurePosixPath(urllib.parse.urlsplit(src).path).name
    if bn not in wanted: continue
    u=urllib.parse.urljoin(hr.url,src)
    rr=get(u); b=rr.content
    ext=pathlib.Path(urllib.parse.urlsplit(rr.url).path).suffix or ".jpg"
    p=OUT/(bn.rsplit(".",1)[0]+ext); p.write_bytes(b)
    im=Image.open(p); im.load(); s1,s256=hh(b)
    rows.append({"panel_file":bn,"panel_label":wanted[bn],"url":rr.url,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256})
if not rows:
    raise RuntimeError("Target images not found")
# contact sheet
tiles=[]
for row in rows:
    im=ImageOps.exif_transpose(Image.open(row["file"])).convert("RGB"); im.thumbnail((600,420))
    t=Image.new("RGB",(640,490),"white"); t.paste(im,((640-im.width)//2,5))
    ImageDraw.Draw(t).text((10,435),f"{row['panel_file']} — {row['panel_label']}\n{row['width']}x{row['height']}",fill="black")
    tiles.append(t)
sheet=Image.new("RGB",(640*len(tiles),490),"white")
for i,t in enumerate(tiles): sheet.paste(t,(i*640,0))
sheet.save(OUT/"contact.jpg",quality=92)
article_text=" ".join(BeautifulSoup(ar.text,"html.parser").stripped_strings)
manifest={"id":118,"target":"Kim Vàng / Barleria lupulina Lindl.",
"article":"Chhabra A, Gupta R. Pharmacognostical Study of Barleria lupulina Lindl. 2025;10(6):91-97.",
"doi":"10.21760/jaims.10.6.13","article_url":ar.url,"inline_url":hr.url,
"article_page_sha1":hh(ab)[0],"article_page_sha256":hh(ab)[1],
"inline_sha1":hh(hb)[0],"inline_sha256":hh(hb)[1],
"license_locked":("Creative Commons Attribution 4.0" in article_text),
"material_basis":"Article states fresh whole-plant parts were procured/authenticated; collected plant material was washed and shade-dried. Figure 1 B/C are fresh adaxial/abaxial leaf surfaces; manuscript §118.5 uses leaves and young shoots fresh.",
"images":rows,"controller_status":"TARGET PANELS ACQUIRED; VISUAL LOCK REQUIRED"}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
