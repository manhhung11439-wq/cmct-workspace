import json,hashlib,pathlib,time,re,html
import requests,fitz

OUT=pathlib.Path("evidence/m5_t1_pd_pharmacognosy_12_15_18"); OUT.mkdir(parents=True,exist_ok=True)
TITLE="File:NLC416-13jh007846-59273 現代本草生藥學.pdf"
EXPECTED="43ac0f2afe93f50a707ed2db727b9c68a2df55e2"
targets={
  12:{"terms":["細辛","细辛","radix asari sieboldi","radix asari"],"name":"Tế Tân","role":"Asarum sieboldii root/rhizome, dried medicinal material"},
  15:{"terms":["桑葉","桑叶","folium mori","morus alba"],"name":"Tang Diệp","role":"Morus alba leaves, dried medicinal material"},
  18:{"terms":["升麻","rhizoma cimicifugae foetidae","cimicifugae foetidae"],"name":"Thăng Ma","role":"Actaea/Cimicifuga foetida rhizome, dried medicinal material"},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/5.4 PD pharmacognosy scout"
api="https://commons.wikimedia.org/w/api.php"
def get(url,params=None):
    last=None
    for i in range(8):
        r=s.get(url,params=params,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get("value") or ""
    v=html.unescape(str(v or "")); v=re.sub(r"<[^>]+>"," ",v); return " ".join(v.split())
meta=get(api,{"action":"query","titles":TITLE,"prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2}).json()
ii=meta["query"]["pages"][0]["imageinfo"][0]; em=ii.get("extmetadata") or {}
pdf=get(ii["url"]).content
s1=hashlib.sha1(pdf).hexdigest(); s256=hashlib.sha256(pdf).hexdigest()
if s1!=EXPECTED: raise SystemExit(f"SHA1 mismatch {s1}")
(OUT/"source_original.pdf").write_bytes(pdf)
doc=fitz.open(stream=pdf,filetype="pdf")
manifest={"source":{"commons_title":TITLE,"url":ii["url"],"sha1":s1,"sha256":s256,"bytes":len(pdf),
  "license":clean(em.get("LicenseShortName")),"credit":clean(em.get("Credit")),"author":clean(em.get("Artist"))},
  "pages":doc.page_count,"targets":{}}
for rid,rec in targets.items():
    hits=[]
    for i,p in enumerate(doc):
        text=" ".join((p.get_text("text") or "").split()).lower()
        matched=[term for term in rec["terms"] if term.lower() in text]
        if matched:
            hits.append({"page":i+1,"terms":matched,"text":text[:1500]})
            pix=p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
            pix.save(str(OUT/f"m5_{rid:03d}_page_{i+1:03d}.png"))
    manifest["targets"][str(rid)]={**rec,"hits":hits}
    print("PD_HITS",rid,json.dumps(hits,ensure_ascii=False),flush=True)
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("SOURCE",json.dumps(manifest["source"],ensure_ascii=False),flush=True)
