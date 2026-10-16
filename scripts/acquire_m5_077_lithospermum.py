import json,hashlib,pathlib,requests,re
from PIL import Image
from io import BytesIO
OUT=pathlib.Path("evidence/m5_t1_077_lithospermum"); OUT.mkdir(parents=True,exist_ok=True)
article="https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2026.1819017/full"
imgurl="https://www.frontiersin.org/files/Articles/1819017/xml-images/fphar-17-1819017-g001.webp"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/6.3 Lithospermum dried root Figure 1"
html=s.get(article,timeout=180); html.raise_for_status(); hb=html.content; (OUT/"article.html").write_bytes(hb)
r=s.get(imgurl,timeout=180); r.raise_for_status(); data=r.content; im=Image.open(BytesIO(data)); im.load()
p=OUT/"figure1_original.webp"; p.write_bytes(data)
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
text=re.sub(r"<[^>]+>"," ",hb.decode("utf-8","ignore")); text=" ".join(text.split())
man={"id":77,"article_url":article,"image_url":r.url,"image_file":str(p),"bytes":len(data),"width":im.width,"height":im.height,"format":im.format,
"sha1":hh(data)[0],"sha256":hh(data)[1],
"license_evidence":"CC BY article; © 2026 Byeon, Ye, Seo and Kwon",
"figure_caption_evidence":"Figure 1A raw material Lithospermum erythrorhizon; article results state dried L. erythrorhizon was extracted"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(man,ensure_ascii=False))
