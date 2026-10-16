# CMCT T1 scientific-figure acquisition v2 for M5 #43 and #53
import io, re, json, hashlib, pathlib, time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image

OUT=pathlib.Path("evidence/m5_t1_scientific_figures_43_53_v2")
OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/2.6 exact JATS figure acquisition"

def get(url,**kw):
    last=None
    for i in range(8):
        r=s.get(url,timeout=120,allow_redirects=True,**kw); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()

def save_img(data,stem):
    with Image.open(io.BytesIO(data)) as im:
        w,h,fmt=im.width,im.height,im.format
    ext={"JPEG":".jpg","PNG":".png","TIFF":".tif","GIF":".gif"}.get(fmt,".img")
    p=OUT/(stem+ext);p.write_bytes(data)
    return p,w,h,fmt,hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()

manifest=[]

# #53 — use Frontiers JATS/XML only
xml_url="https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2021.685575/xml"
xml=get(xml_url).text
(OUT/"frontiers_685575.xml").write_text(xml,encoding="utf-8")
xs=BeautifulSoup(xml,"xml")
fig53=None
for f53 in xs.find_all("fig"):
    label=" ".join(f53.find("label").stripped_strings) if f53.find("label") else ""
    cap=" ".join(f53.find("caption").stripped_strings) if f53.find("caption") else ""
    if (re.search(r"\b(FIGURE|FIG\.?)[ ]*1\b",label,re.I) or
        ("dried root" in cap.lower() and "transverse" in cap.lower())):
        fig53=f53;break
if fig53 is None: raise RuntimeError("Frontiers exact Figure 1 not found in XML")
cap53=" ".join(fig53.find("caption").stripped_strings) if fig53.find("caption") else ""
graphics=fig53.find_all(["graphic","media"])
hrefs=[]
for g in graphics:
    for key in ("xlink:href","href"):
        if g.get(key): hrefs.append(g.get(key))
if not hrefs: raise RuntimeError("Frontiers Figure 1 has no graphic href: "+str(fig53)[:1500])
# Resolve current Frontiers HTML/CDN path plus legacy static paths.
article_html=get("https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2021.685575/full").text
hs=BeautifulSoup(article_html,"html.parser")
html_urls=[]
for tag in hs.find_all(["img","source"]):
    vals=[]
    for key in ("src","data-src","srcset","data-srcset"):
        if tag.get(key): vals.append(tag.get(key))
    for val in vals:
        for part in str(val).split(","):
            u=part.strip().split()[0]
            if "685575" in u or "g001" in u:
                html_urls.append(urljoin("https://www.frontiersin.org/",u))
print("FRONTIERS_HTML_MATCHES",html_urls,flush=True)
stem="fphar-12-685575-g001"
legacy=[
 f"https://www.frontiersin.org/files/Articles/685575/fphar-12-685575-HTML/image_m/{stem}.jpg",
 f"https://www.frontiersin.org/files/Articles/685575/fphar-12-685575-HTML/image_l/{stem}.jpg",
 f"https://www.frontiersin.org/files/Articles/685575/fphar-12-685575-HTML/image_n/{stem}.jpg",
 f"https://www.frontiersin.org/files/Articles/685575/fphar-12-685575-HTML/image_t/{stem}.jpg",
 f"https://www.frontiersin.org/files/Articles/685575/fphar-12-685575-HTML/image_m/{stem}.tif",
 f"https://www.frontiersin.org/files/Articles/685575/fphar-12-685575-HTML/image_l/{stem}.tif",
]
cands=[]
test_urls=list(dict.fromkeys(html_urls+legacy+[urljoin(xml_url,h) for h in hrefs]))
for u in test_urls:
    try:
        rr=get(u); data=rr.content
        with Image.open(io.BytesIO(data)) as im: wh=(im.width,im.height,im.format)
        print("FRONTIERS_IMAGE_OK",u,len(data),wh,flush=True)
        cands.append((im.width*im.height,len(data),u,data,wh))
    except Exception as e:
        print("FRONTIERS_IMAGE_FAIL",u,type(e).__name__,str(e)[:200],flush=True)
if not cands:
    raise RuntimeError("Could not download Frontiers Figure 1; tested="+repr(test_urls[:50]))
_,_,u53,data53,_=max(cands,key=lambda x:(x[0],x[1]))
p,w,h,fmt,s1,s256=save_img(data53,"m5_053_frontiers_fig1_original")
manifest.append({"id":53,"figure":"Figure 1","article":"https://doi.org/10.3389/fphar.2021.685575",
 "asset_url":u53,"caption":cap53,"file":str(p),"bytes":len(data53),"width":w,"height":h,
 "format":fmt,"sha1":s1,"sha256":s256,"license":"CC BY","authors":"Nie et al. 2021"})

# #43 — parse Springer exact figure caption, then full-size media source
article43="https://link.springer.com/article/10.1007/s11434-016-1136-5"
html43=get(article43).text
(OUT/"springer_1136_5.html").write_text(html43,encoding="utf-8")
sp=BeautifulSoup(html43,"html.parser")
fig43=None
for fg in sp.find_all(["figure","div"]):
    txt=" ".join(fg.stripped_strings)
    if "dried root" in txt.lower() and "scutellaria" in txt.lower():
        # require local figure-ish structure
        img=fg.find("img")
        if img:
            fig43=(fg,img,txt);break
if fig43 is None:
    for img in sp.find_all("img"):
        alt=" ".join([img.get("alt") or "",img.get("title") or ""])
        if "fig" in alt.lower() and ("scutellaria" in alt.lower() or "medicinal" in alt.lower()):
            fig43=(img.parent,img,alt);break
if fig43 is None: raise RuntimeError("Springer Fig 1 container not resolved")
fg,img43,txt43=fig43
urls=[]
for attr in ("src","data-src","data-original"):
    if img43.get(attr): urls.append(img43.get(attr))
for attr in ("srcset","data-srcset"):
    val=img43.get(attr)
    if val:
        for part in val.split(","):
            urls.append(part.strip().split()[0])
pic=img43.find_parent("picture")
if pic:
    for src in pic.find_all("source"):
        val=src.get("srcset") or src.get("data-srcset")
        if val:
            for part in val.split(","): urls.append(part.strip().split()[0])
# transform Springer media URLs to original/full when possible
more=[]
for u in urls:
    if not u: continue
    absu=urljoin(article43,u)
    more.extend([absu,
      absu.replace("/small/","/full/").replace("/medium/","/full/"),
      absu.replace("springer-static/image/","springer-static/image/")])
urls=list(dict.fromkeys(more))
cands=[]
for u in urls:
    try:
        rr=get(u); data=rr.content
        with Image.open(io.BytesIO(data)) as im: wh=(im.width,im.height,im.format)
        cands.append((im.width*im.height,len(data),u,data,wh))
    except Exception:
        pass
if not cands: raise RuntimeError("No downloadable Springer figure image URLs: "+repr(urls[:20]))
_,_,u43,data43,_=max(cands,key=lambda x:(x[0],x[1]))
p,w,h,fmt,s1,s256=save_img(data43,"m5_043_springer_fig1_original")
manifest.append({"id":43,"figure":"Figure 1","article":"https://doi.org/10.1007/s11434-016-1136-5",
 "asset_url":u43,"caption":txt43[:2000],"file":str(p),"bytes":len(data43),"width":w,"height":h,
 "format":fmt,"sha1":s1,"sha256":s256,"license":"CC BY 4.0",
 "authors":"Zhao, Chen & Martin 2016"})

(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("CMCT_SCI_FIG_MANIFEST="+json.dumps(manifest,ensure_ascii=False))
