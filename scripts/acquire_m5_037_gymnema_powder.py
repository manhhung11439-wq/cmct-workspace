import json,hashlib,pathlib,time,requests,html,re,urllib.parse
from bs4 import BeautifulSoup
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_037_gymnema_powder"); OUT.mkdir(parents=True,exist_ok=True)
URL="https://www.actabotanica.org/phytochemical-screening-and-pharmacognostic-studies-and-antidiabetic-activity-of-meshashringi-gymnema-sylvestre-retz-r-br-ex-sm-leaf-and-stem-components/"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/32.1 Gymnema exact dried powder acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
r=get(URL); hb=r.content; (OUT/"article.html").write_bytes(hb)
soup=BeautifulSoup(r.text,"html.parser")
cands=[]
for im in soup.find_all("img"):
    src=im.get("src") or im.get("data-src") or im.get("data-lazy-src")
    if not src: continue
    alt=(im.get("alt") or "")+" "+(im.get("title") or "")
    parent=" ".join(im.parent.stripped_strings) if im.parent else ""
    score=0
    txt=(alt+" "+parent).lower()
    if "figure 1" in txt or "plant powder" in txt or "gymnema" in txt: score+=10
    if "fig" in src.lower(): score+=2
    cands.append((score,urllib.parse.urljoin(r.url,html.unescape(src)),alt,parent[:500]))
cands=sorted(cands,reverse=True)
assets=[]
for score,u,alt,parent in cands[:30]:
    try:
        ir=get(u); ct=(ir.headers.get("content-type") or "").lower()
        if not ct.startswith("image/"): continue
        ext=".png" if "png" in ct else ".jpg" if ("jpeg" in ct or "jpg" in ct) else pathlib.Path(urllib.parse.urlparse(ir.url).path).suffix or ".img"
        fp=OUT/f"asset_{len(assets)+1:02d}{ext}"; fp.write_bytes(ir.content)
        try:
            im=Image.open(fp); im.load()
        except: continue
        if im.width<250 or im.height<150: continue
        s1,s256=hh(ir.content)
        row={"score":score,"url":ir.url,"alt":alt,"parent":parent,"file":str(fp),"bytes":len(ir.content),"width":im.width,"height":im.height,"format":im.format,"sha1":s1,"sha256":s256}
        assets.append(row); print("ASSET="+json.dumps(row,ensure_ascii=False),flush=True)
    except Exception as e:
        pass
text=" ".join(soup.stripped_strings)
ctx=[]
for needle in ["shade-dried", "Morphology of dried plant material", "Plant powder sample", "Creative Commons Attribution"]:
    k=text.lower().find(needle.lower())
    if k>=0: ctx.append(text[max(0,k-900):k+1700])
man={"id":37,"target":"Dây Thìa Canh / Gymnema sylvestre (Retz.) R.Br. ex Schult.",
"article_url":r.url,"article_bytes":len(hb),"article_sha1":hh(hb)[0],"article_sha256":hh(hb)[1],
"license":"CC BY 4.0 per article copyright notice","assets":assets,"contexts":ctx,
"controller_rule":"Promote only Figure 1A if it is visibly the dried leaf+stem powder sample described by article; crop-only, no retouch."}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY="+json.dumps({"assets":assets,"contexts":ctx},ensure_ascii=False),flush=True)
