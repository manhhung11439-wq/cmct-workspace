import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/m5_t1_target_missing_4_32"); OUT.mkdir(parents=True,exist_ok=True)
targets={
4:{"taxon":"Bupleurum chinense","terms":["Bupleurum chinense dried root","Bupleuri Radix","柴胡 中药","柴胡 藥材"],"role":["root","radix","dried","柴胡","药材","藥材"]},
5:{"taxon":"Notopterygium incisum","terms":["Notopterygium incisum dried rhizome root","Notopterygii Rhizoma et Radix","羌活 中药","羌活 藥材"],"role":["root","rhizome","dried","羌活"]},
6:{"taxon":"Saposhnikovia divaricata","terms":["Saposhnikovia divaricata dried root","Saposhnikoviae Radix","防风 中药","防風 藥材"],"role":["root","radix","dried","防风","防風"]},
8:{"taxon":"Cinnamomum cassia","terms":["Cinnamomum cassia dried twig","Cinnamomi Ramulus","桂枝 中药","桂枝 藥材"],"role":["twig","ramulus","branch","dried","桂枝"]},
9:{"taxon":"Schizonepeta tenuifolia","terms":["Schizonepeta tenuifolia dried aerial herb","Schizonepetae Herba","荆芥 中药","荊芥 藥材"],"role":["aerial","herb","dried","荆芥","荊芥"]},
10:{"taxon":"Mentha canadensis","terms":["Mentha canadensis dried aerial herb","Menthae Haplocalycis Herba","薄荷 中药","薄荷 藥材"],"role":["aerial","herb","dried","薄荷"]},
12:{"taxon":"Asarum sieboldii","terms":["Asarum sieboldii dried root rhizome","Asari Radix et Rhizoma","细辛 中药","細辛 藥材"],"role":["root","rhizome","dried","细辛","細辛"]},
15:{"taxon":"Morus alba","terms":["Morus alba dried leaves medicinal","Mori Folium","桑叶 中药","桑葉 藥材"],"role":["leaf","leaves","folium","dried","桑叶","桑葉"]},
18:{"taxon":"Actaea cimicifuga","terms":["Actaea cimicifuga dried rhizome","Cimicifugae Rhizoma","升麻 中药","升麻 藥材"],"role":["rhizome","dried","升麻"]},
19:{"taxon":"Cryptotympana atrata","terms":["Cryptotympana atrata exuviae","Cicadae Periostracum","蝉蜕 中药","蟬蛻 藥材"],"role":["exuviae","exuvia","slough","periostracum","蝉蜕","蟬蛻"]},
21:{"taxon":"Elsholtzia ciliata","terms":["Elsholtzia ciliata dried aerial herb","Elsholtziae Herba","香薷 中药","香薷 藥材"],"role":["aerial","herb","dried","香薷"]},
22:{"taxon":"Centipeda minima","terms":["Centipeda minima dried whole herb","Centipedae Herba","鹅不食草 中药","鵝不食草 藥材"],"role":["whole plant","herb","dried","鹅不食草","鵝不食草"]},
23:{"taxon":"Vitex trifolia","terms":["Vitex trifolia dried fruit medicinal","Viticis Fructus","蔓荆子 中药","蔓荊子 藥材"],"role":["fruit","fructus","dried","蔓荆子","蔓荊子"]},
24:{"taxon":"Spirodela polyrhiza","terms":["Spirodela polyrhiza dried whole plant medicinal","Spirodelae Herba","浮萍 中药","浮萍 藥材"],"role":["whole plant","herb","dried","浮萍"]},
25:{"taxon":"Glycine max","terms":["medicinal fermented soybean Douchi","Sojae Semen Praeparatum","淡豆豉 中药","淡豆豉 藥材"],"role":["fermented","soybean","semen praeparatum","淡豆豉","medicinal"]},
27:{"taxon":"Ligusticum sinense","terms":["Ligusticum sinense dried rhizome root","Ligustici Rhizoma et Radix","藁本 中药","藁本 藥材"],"role":["root","rhizome","dried","藁本"]},
30:{"taxon":"Citrus aurantiifolia","terms":["Citrus aurantiifolia harvested fresh leaves","Citrus aurantiifolia picked leaves","lime leaves market"],"role":["leaf","leaves","fresh","picked","harvested"]},
31:{"taxon":"Vitex negundo","terms":["Vitex negundo harvested leaves medicinal","Vitex negundo dried leaves medicinal","Viticis Negundi Folium"],"role":["leaf","leaves","fresh","dried","harvested"]},
32:{"taxon":"Kyllinga nemoralis","terms":["Kyllinga nemoralis dried whole herb","Kyllinga nemoralis medicinal herb","dried Kyllinga herb"],"role":["whole plant","herb","dried"]},
}
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.8 targeted missing M5 4-32"
api="https://commons.wikimedia.org/w/api.php"
def get(params):
  last=None
  for i in range(8):
    r=s.get(api,params=params,timeout=90); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(int(r.headers.get("Retry-After") or min(60,3*(2**i)))); continue
    r.raise_for_status(); return r.json()
  last.raise_for_status()
def clean(v):
  if isinstance(v,dict): v=v.get("value") or ""
  v=html.unescape(str(v or "")); v=re.sub(r"<[^>]+>"," ",v)
  return " ".join(v.split())
allout={}
for rid,t in targets.items():
  seen={}; qs=[]
  for term in t["terms"]:
    data=get({"action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,"gsrlimit":35,
              "prop":"imageinfo","iiprop":"url|sha1|size|extmetadata","iiurlwidth":900,
              "format":"json","formatversion":2})
    pages=data.get("query",{}).get("pages",[]); qs.append({"term":term,"count":len(pages)})
    for p in pages:
      ii=(p.get("imageinfo") or [{}])[0]; em=ii.get("extmetadata") or {}
      def e(k): return clean(em.get(k) or "")
      title=p.get("title") or ""
      seen[title]={"title":title,"url":ii.get("url"),"sha1":ii.get("sha1"),"width":ii.get("width"),
                   "height":ii.get("height"),"size":ii.get("size"),"license":e("LicenseShortName"),
                   "license_url":e("LicenseUrl"),"author":e("Artist"),"credit":e("Credit"),
                   "description":e("ImageDescription"),"categories":e("Categories")}
    time.sleep(.4)
  def score(x):
    blob=" ".join(str(x.get(k) or "") for k in ("title","description","categories")).lower()
    sc=12 if t["taxon"].lower() in blob else 0
    sc+=sum(4 for z in t["role"] if z.lower() in blob)
    if any(z in blob for z in ["medicinal","herbal medicine","chinese medicine","materia medica","crude drug","kampo"]): sc+=7
    if any(z in blob for z in ["herbarium","pressed specimen","illustration","woodcut","pdf","djvu","living plant","flowering plant"]): sc-=12
    lic=(x.get("license") or "").lower()
    if any(z in lic for z in ["cc0","cc by","public domain","no restrictions"]): sc+=5
    if x.get("url") and x.get("sha1"): sc+=2
    return sc
  vals=sorted(seen.values(),key=lambda x:(-score(x),x["title"]))
  for x in vals:x["score"]=score(x)
  allout[str(rid)]={"target":t,"queries":qs,"candidates":vals[:50]}
  print(rid,t["taxon"],"unique",len(vals),"top",[(v["score"],v["title"],v["license"],v["author"][:60]) for v in vals[:10]],flush=True)
(OUT/"candidates.json").write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding="utf-8")
