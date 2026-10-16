import requests,bs4,pathlib,json,hashlib,time,urllib.parse,re
OUT=pathlib.Path("evidence/m5_t1_044_coptis"); OUT.mkdir(parents=True,exist_ok=True)
url="https://pmc.ncbi.nlm.nih.gov/articles/PMC4820238/"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.1 exact Coptis dried-rhizome figure"
def get(u):
  last=None
  for i in range(7):
    r=s.get(u,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(30,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
html=get(url).text
soup=bs4.BeautifulSoup(html,"html.parser")
target=None
for fig in soup.find_all("figure"):
  cap=fig.find("figcaption")
  txt=cap.get_text(" ",strip=True) if cap else ""
  if "Coptis chinensis" in txt and "dried rhizome" in txt:
    target=(fig,txt); break
if not target: raise RuntimeError("target figure not found")
fig,caption=target
img=fig.find("img")
src=img.get("data-src") or img.get("src")
imgurl=urllib.parse.urljoin(url,src)
r=get(imgurl); data=r.content
ct=r.headers.get("content-type","")
ext=".jpg" if "jpeg" in ct else ".png" if "png" in ct else ".bin"
p=OUT/("coptis_fig1_original"+ext); p.write_bytes(data)
s1=hashlib.sha1(data).hexdigest(); s256=hashlib.sha256(data).hexdigest()
manifest={"id":44,"article_url":url,"caption":caption,"figure_url":r.url,"content_type":ct,
          "original_file":str(p),"bytes":len(data),"sha1":s1,"sha256":s256,
          "license":"CC BY 4.0 (PLOS ONE article license; verify article page license statement)"}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_044_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
