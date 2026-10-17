import json,hashlib,pathlib,time,requests,html,re
import fitz
OUT=pathlib.Path('evidence/pd_atlas_yaowu_tukao_v2'); OUT.mkdir(parents=True,exist_ok=True)
TITLE='File:NLC416-08jh011487-25896 藥物圖考 第2卷.pdf'
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/29.3 PD Yaowu Tukao atlas scout'
def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=240,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get('value','')
    return re.sub(r'<[^>]+>','',html.unescape(str(v))).strip()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
q=get('https://commons.wikimedia.org/w/api.php',{
 'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','titles':TITLE
}).json()
p=next(iter(q['query']['pages'].values())); ii=p['imageinfo'][0]; meta=ii.get('extmetadata',{})
b=get(ii['url']).content; pdf=OUT/'yaowu_tukao_v2.pdf'; pdf.write_bytes(b)
s1,s256=hh(b)
doc=fitz.open(stream=b,filetype='pdf')
terms=['白薇','地骨皮','黃蘗','黄蘗','黃柏','黄柏']
hits={t:[] for t in terms}
texts=[]
for i,page in enumerate(doc):
    txt=page.get_text('text')
    texts.append(txt)
    for t in terms:
        if t in txt: hits[t].append(i+1)
# Render pages around any exact text-layer hit; if none, render TOC-heavy first 30 pages as contact sheets for visual controller.
render_pages=set()
for arr in hits.values():
    for pn in arr:
        render_pages.update(range(max(1,pn-1),min(len(doc),pn+1)+1))
if not render_pages:
    render_pages.update(range(1,min(len(doc),30)+1))
previews=[]
for pn in sorted(render_pages):
    page=doc[pn-1]
    pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False)
    out=OUT/f'page_{pn:04d}.jpg'; pix.save(out,jpg_quality=88)
    previews.append(str(out))
man={'title':TITLE,'pageid':p.get('pageid'),'original_url':ii['url'],'api_sha1':ii.get('sha1'),
     'local_sha1':s1,'local_sha256':s256,'bytes':len(b),'pages':len(doc),
     'license_short':clean(meta.get('LicenseShortName','')),'license_url':clean(meta.get('LicenseUrl','')),
     'description':clean(meta.get('ImageDescription','')),'author':clean(meta.get('Artist','')),
     'hits':hits,'render_pages':sorted(render_pages),'previews':previews,
     'controller_note':'Text extraction only, no OCR. If no exact text-layer hits, rendered pages require visual inspection.'}
assert s1==ii.get('sha1'),(s1,ii.get('sha1'))
(OUT/'manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf-8')
print('MANIFEST='+json.dumps(man,ensure_ascii=False),flush=True)
