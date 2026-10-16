import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_japanese_drugname_4_32"); OUT.mkdir(parents=True,exist_ok=True)
targets={
4:{"terms":["サイコ 生薬","柴胡 生薬","Bupleurum root crude drug"],"taxon":"Bupleurum chinense"},
5:{"terms":["キョウカツ 生薬","羌活 生薬","Notopterygium crude drug"],"taxon":"Notopterygium incisum"},
6:{"terms":["ボウフウ 生薬","防風 生薬","Saposhnikovia crude drug"],"taxon":"Saposhnikovia divaricata"},
8:{"terms":["ケイシ 生薬","桂枝 生薬","Cinnamomum cassia ramulus crude drug"],"taxon":"Cinnamomum cassia"},
9:{"terms":["ケイガイ 生薬","荊芥 生薬","Schizonepeta crude drug"],"taxon":"Schizonepeta tenuifolia"},
10:{"terms":["ハッカ 生薬","薄荷 生薬","Mentha canadensis crude drug"],"taxon":"Mentha canadensis"},
12:{"terms":["サイシン 生薬","細辛 生薬","Asarum root rhizome crude drug"],"taxon":"Asarum sieboldii"},
18:{"terms":["ショウマ 生薬","升麻 生薬","Cimicifuga rhizome crude drug"],"taxon":"Actaea cimicifuga"},
23:{"terms":["マンケイシ 生薬","蔓荊子 生薬","Vitex fruit crude drug"],"taxon":"Vitex trifolia"},
24:{"terms":["フヒョウ 生薬","浮萍 生薬","Spirodela crude drug"],"taxon":"Spirodela polyrhiza"},
27:{"terms":["コウホン 生薬","藁本 生薬","Ligusticum crude drug"],"taxon":"Ligusticum sinense"},
}
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/1.7 Japanese crude drug search"
api="https://commons.wikimedia.org/w/api.php"
def clean(v):
 if isinstance(v,dict):v=v.get("value") or ""
 v=html.unescape(str(v or ""));v=re.sub(r"<[^>]+>"," ",v)
 return " ".join(v.split())
def get(params):
 last=None
 for i in range(8):
  r=s.get(api,params=params,timeout=90);last=r
  if r.status_code in (429,500,502,503,504):
   time.sleep(int(r.headers.get("Retry-After") or min(60,3*(2**i))));continue
  r.raise_for_status();return r.json()
 last.raise_for_status()
out={}
for rid,t in targets.items():
 seen={}
 for term in t["terms"]:
  data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":50,
    "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2})
  for p in data.get("query",{}).get("pages",[]):
   ii=(p.get("imageinfo") or [{}])[0];em=ii.get("extmetadata") or {}
   def e(k):return clean(em.get(k) or "")
   title=p.get("title") or ""
   seen[title]={"title":title,"url":ii.get("url"),"sha1":ii.get("sha1"),"size":ii.get("size"),
    "width":ii.get("width"),"height":ii.get("height"),"license":e("LicenseShortName"),
    "license_url":e("LicenseUrl"),"author":e("Artist"),"credit":e("Credit"),
    "description":e("ImageDescription"),"categories":e("Categories")}
  time.sleep(.55)
 def score(x):
  b=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
  sc=0
  if t["taxon"].lower() in b:sc+=12
  if "生薬" in b or "crude drug" in b or "herbal medicine" in b:sc+=10
  if any(z in b for z in ["root","rhizome","twig","fruit","herb","dried"]):sc+=4
  if any(z in b for z in [".pdf",".djvu","herbarium","illustration","living plant"]):sc-=14
  lic=(x.get("license") or "").lower()
  if any(z in lic for z in ["cc0","cc by","public domain"]):sc+=5
  if x.get("url") and x.get("sha1"):sc+=2
  return sc
 vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
 for x in vals:x["score"]=score(x)
 out[str(rid)]={"target":t,"candidates":vals[:60]}
 print("TARGET",rid,"UNIQUE",len(vals),"TOP",[(v["score"],v["title"],v["license"],v["description"][:120]) for v in vals[:15]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
