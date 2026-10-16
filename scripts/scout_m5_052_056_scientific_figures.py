import json, pathlib, hashlib, re, time, urllib.parse
import requests
from bs4 import BeautifulSoup

OUT=pathlib.Path("evidence/m5_t1_052_056_scientific_scout"); OUT.mkdir(parents=True,exist_ok=True)
articles={
  52:{
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC13295379/",
    "taxon":"Taraxacum mongolicum",
    "need":["dried whole plant","whole plant","plant material","dandelion"]
  },
  56:{
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC11590933/",
    "taxon":"Lycium chinense",
    "need":["root bark","Lycii Radicis Cortex","plant material","Lycium chinense"]
  }
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.0 scientific figure scout"
def get(url,attempts=7):
  last=None
  for i in range(attempts):
    r=s.get(url,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(30,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
def hashes(data): return hashlib.sha1(data).hexdigest(),hashlib.sha256(data).hexdigest()
allout={}
for rid,a in articles.items():
  html=get(a["url"]).text
  (OUT/f"{rid}_article.html").write_text(html,encoding="utf-8")
  soup=BeautifulSoup(html,"html.parser")
  title=(soup.find("h1") or soup.find("title"))
  record={"id":rid,"url":a["url"],"title":title.get_text(" ",strip=True) if title else "","figures":[]}
  figs=soup.find_all("figure")
  for ix,fig in enumerate(figs,1):
    cap=fig.find("figcaption")
    captext=cap.get_text(" ",strip=True) if cap else ""
    imgs=fig.find_all("img")
    imgout=[]
    for j,img in enumerate(imgs,1):
      src=img.get("data-src") or img.get("src") or ""
      if not src: continue
      url=urllib.parse.urljoin(a["url"],src)
      try:
        rr=get(url); data=rr.content
        ext=".jpg"
        ct=(rr.headers.get("content-type") or "").lower()
        if "png" in ct: ext=".png"
        elif "tif" in ct: ext=".tif"
        elif "gif" in ct: ext=".gif"
        fn=f"{rid}_fig{ix}_{j}{ext}"
        (OUT/fn).write_bytes(data)
        s1,s256=hashes(data)
        imgout.append({"file":fn,"url":rr.url,"bytes":len(data),"sha1":s1,"sha256":s256,
                       "alt":img.get("alt") or "","content_type":ct})
      except Exception as e:
        imgout.append({"url":url,"error":repr(e),"alt":img.get("alt") or ""})
    blob=(captext+" "+" ".join(x.get("alt","") for x in imgout)).lower()
    score=sum(1 for term in a["need"] if term.lower() in blob)
    rec={"index":ix,"caption":captext,"images":imgout,"need_score":score}
    record["figures"].append(rec)
    print("FIG",rid,ix,"score",score,"caption",captext[:500],flush=True)
    for x in imgout: print("IMG",rid,ix,x,flush=True)
  allout[str(rid)]=record
(OUT/"manifest.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
print("SCOUT_SUMMARY="+json.dumps({k:[{"i":f["index"],"s":f["need_score"],"c":f["caption"][:250]} for f in v["figures"]] for k,v in allout.items()},ensure_ascii=False),flush=True)
