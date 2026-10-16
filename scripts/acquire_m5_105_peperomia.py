import requests,bs4,pathlib,json,hashlib,time,urllib.parse
OUT=pathlib.Path("evidence/m5_t1_105_peperomia"); OUT.mkdir(parents=True,exist_ok=True)
url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11637809/"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/4.8 exact Peperomia harvested-material figure"
def get(u):
  last=None
  for i in range(8):
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
  if "Botanical characteristics of Peperomia pellucida" in txt:
    target=(fig,txt); break
if not target:
  # PMC layouts can wrap figure in divs; locate caption text then nearest parent containing img
  node=soup.find(string=lambda x:x and "Botanical characteristics of Peperomia pellucida" in x)
  if node:
    par=node.parent
    for _ in range(8):
      if par is None: break
      img=par.find("img")
      if img:
        target=(par,par.get_text(" ",strip=True)); break
      par=par.parent
if not target: raise RuntimeError("Peperomia Fig1 not found")
fig,caption=target
img=fig.find("img")
src=img.get("data-src") or img.get("src")
r=get(urllib.parse.urljoin(url,src)); data=r.content
ct=(r.headers.get("content-type") or "").lower()
ext=".jpg" if "jpeg" in ct else ".png" if "png" in ct else ".bin"
p=OUT/("peperomia_fig1_original"+ext); p.write_bytes(data)
s1=hashlib.sha1(data).hexdigest(); s256=hashlib.sha256(data).hexdigest()
manifest={"id":105,"article_url":url,"pmcid":"PMC11637809","caption":caption,
 "identity":"Peperomia pellucida (L.) Kunth","material_context":"plants collected/harvested in Can Tho City, Vietnam; washed; damaged parts removed",
 "license":"CC BY","figure_url":r.url,"file":str(p),"bytes":len(data),"sha1":s1,"sha256":s256}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_105_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
