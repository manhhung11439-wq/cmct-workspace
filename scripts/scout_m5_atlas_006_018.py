import io,json,hashlib,pathlib,time,re
import requests,fitz
from PIL import Image,ImageDraw

OUT=pathlib.Path("evidence/m5_t1_atlas_006_018"); OUT.mkdir(parents=True,exist_ok=True)
title="File:NLC416-08jh015896-38387 中國藥物標本圖影.pdf"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/5.2 PD Chinese crude-drug atlas exact page scout"
api="https://commons.wikimedia.org/w/api.php"

def get(url,params=None):
    last=None
    for i in range(8):
        r=s.get(url,params=params,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()

meta=get(api,{"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2}).json()
p=meta["query"]["pages"][0]; ii=p["imageinfo"][0]; url=ii["url"]
r=get(url); pdf=r.content
(OUT/"atlas_original.pdf").write_bytes(pdf)
ps1,ps256=hh(pdf)
doc=fitz.open(stream=pdf,filetype="pdf")

targets={6:["防風","防风"],8:["桂枝"],9:["荊芥","荆芥"],10:["薄荷"],12:["細辛","细辛"],15:["桑葉","桑叶"],18:["升麻"]}
hits={}
for rid,names in targets.items():
    rh=[]
    for i,page in enumerate(doc):
        txt=" ".join(page.get_text("text").split())
        found=[n for n in names if n in txt]
        if found:
            rh.append({"page":i+1,"found":found,"text":txt[:800]})
    hits[str(rid)]=rh
    print("ATLAS_HITS",rid,json.dumps(rh,ensure_ascii=False),flush=True)

# Render exact-hit pages at 160 dpi for visual controller. Deduplicate pages.
pages=sorted({h["page"] for hs in hits.values() for h in hs})
renders=[]
for pg in pages:
    page=doc[pg-1]
    pix=page.get_pixmap(matrix=fitz.Matrix(160/72,160/72),alpha=False)
    fn=OUT/f"atlas_page_{pg:03d}.png"; pix.save(str(fn))
    b=fn.read_bytes(); s1,s256=hh(b)
    renders.append({"page":pg,"file":str(fn),"w":pix.width,"h":pix.height,"bytes":len(b),"sha1":s1,"sha256":s256})

# Contact sheet small
thumbs=[]
for rec in renders:
    im=Image.open(rec["file"]).convert("RGB"); im.thumbnail((500,700)); thumbs.append((rec,im.copy()))
if thumbs:
    cols=3; cellw=520; cellh=760; rows=(len(thumbs)+cols-1)//cols
    sh=Image.new("RGB",(cols*cellw,rows*cellh),"white"); dr=ImageDraw.Draw(sh)
    for idx,(rec,im) in enumerate(thumbs):
        x=(idx%cols)*cellw; y=(idx//cols)*cellh
        dr.text((x+5,y+5),f"PDF page {rec['page']}",fill="black"); sh.paste(im,(x+5,y+35))
    sh.save(OUT/"atlas_hit_contact_sheet.jpg",quality=88)

manifest={"commons_title":title,"resolved_url":url,"commons_sha1":ii.get("sha1"),
          "pdf_bytes":len(pdf),"pdf_sha1":ps1,"pdf_sha256":ps256,"num_pages":doc.page_count,
          "targets":targets,"hits":hits,"renders":renders,
          "source_note":"1935 Chinese drug specimen image atlas; Commons/National Library of China; file page marked Republican-era public-domain upload."}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("ATLAS_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
