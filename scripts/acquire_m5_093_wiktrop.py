import re,json,hashlib,pathlib,time,requests,html as ihtml
from bs4 import BeautifulSoup
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_093_wiktrop"); OUT.mkdir(parents=True,exist_ok=True)
PAGE="https://portal.wiktrop.org/group/Bananier/observation/show/5949"
IMG="https://portal.wiktrop.org/files-api/api/get/raw/observations/3849fd10-73d6-4e54-beaa-6136a5caa751/433.jpg"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/29.0 Bidens pilosa WIKTROP exact observation"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=120,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(30,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
pr=get(PAGE); hb=pr.content; (OUT/"observation.html").write_bytes(hb)
txt=pr.text
soup=BeautifulSoup(txt,"html.parser")
plain="\n".join(x.strip() for x in soup.stripped_strings)
# capture license-related snippets and CC urls/classes
lines=[x for x in plain.splitlines() if re.search(r"license|creative commons|CC[_ -]?BY|attribution|non.?commercial|share.?alike",x,re.I)]
links=[]
for a in soup.find_all("a",href=True):
    href=a["href"]
    label=" ".join(a.stripped_strings)
    if re.search(r"creativecommons|license",href,re.I) or re.search(r"license|creative commons|CC",label,re.I):
        links.append({"text":label,"href":href})
# broad script/json contexts around observation id and license
contexts=[]
for pat in ["license","creative","5949","3849fd10-73d6-4e54-beaa-6136a5caa751"]:
    for m in re.finditer(pat,txt,re.I):
        contexts.append(txt[max(0,m.start()-500):m.end()+700])
        if len(contexts)>20: break
    if len(contexts)>20: break
ir=get(IMG); b=ir.content
p=OUT/"m5_093_Bidens_pilosa_uprooted_fresh.jpg"; p.write_bytes(b)
im=Image.open(p); im.load(); s1,s256=hh(b)
man={
"id":93,"target":"Đơn Buốt / Bidens pilosa L.","observation_page":PAGE,"page_final_url":pr.url,
"page_sha1":hh(hb)[0],"page_sha256":hh(hb)[1],
"page_title":soup.title.get_text(" ",strip=True) if soup.title else "",
"license_lines":lines,"license_links":links,"html_contexts":contexts,
"image_url":ir.url,"image_file":str(p),"image_bytes":len(b),"width":im.width,"height":im.height,"format":im.format,
"image_sha1":s1,"image_sha256":s256,
"controller_status":"IMAGE + OBSERVATION HTML ACQUIRED; FILE/OBSERVATION LICENSE MUST BE EXPLICITLY COMMERCIAL-SAFE BEFORE PROMOTION"
}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("LICENSE_LINES="+json.dumps(lines,ensure_ascii=False),flush=True)
print("LICENSE_LINKS="+json.dumps(links,ensure_ascii=False),flush=True)
print("MANIFEST_SUMMARY="+json.dumps({k:v for k,v in man.items() if k!="html_contexts"},ensure_ascii=False),flush=True)
