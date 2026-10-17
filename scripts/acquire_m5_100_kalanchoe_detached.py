import json,hashlib,pathlib,time,requests,html,re
from PIL import Image
OUT=pathlib.Path('evidence/m5_t1_100_kalanchoe_detached'); OUT.mkdir(parents=True,exist_ok=True)
titles=[
 'File:Bouturage naturel sur feuille de Kalanchoe pinnata.jpg',
 'File:Propagation of kalanchoe pinnata.jpg',
 'File:Kalanchoe-pinnata veg reprod.jpg',
]
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/29.1 Kalanchoe detached-leaf acquisition'
def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504): time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get('value','')
    return re.sub(r'<[^>]+>','',html.unescape(str(v))).strip()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
rows=[]
for i,title in enumerate(titles,1):
    q=get('https://commons.wikimedia.org/w/api.php',{'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','titles':title}).json()
    p=next(iter(q['query']['pages'].values()))
    if 'imageinfo' not in p:
        rows.append({'title':title,'error':'no imageinfo'}); continue
    ii=p['imageinfo'][0]; meta=ii.get('extmetadata',{})
    b=get(ii['url']).content
    ext=pathlib.Path(ii['url'].split('?')[0]).suffix or '.jpg'
    fn=OUT/f'candidate_{i:02d}{ext}'; fn.write_bytes(b)
    im=Image.open(fn); im.load(); s1,s256=hh(b)
    row={'id':100,'target':'Kalanchoe pinnata (Lam.) Pers.','title':title,'canonical_title':p.get('title'),'pageid':p.get('pageid'),
      'original_url':ii['url'],'api_sha1':ii.get('sha1'),'local_sha1':s1,'local_sha256':s256,'bytes':len(b),'width':im.width,'height':im.height,'format':im.format,'file':str(fn),
      'description':clean(meta.get('ImageDescription','')),'author':clean(meta.get('Artist','')),'credit':clean(meta.get('Credit','')),
      'license_short':clean(meta.get('LicenseShortName','')),'license_url':clean(meta.get('LicenseUrl','')),'usage_terms':clean(meta.get('UsageTerms','')),
      'copyrighted':clean(meta.get('Copyrighted','')),'categories':clean(meta.get('Categories',''))}
    if ii.get('sha1'): assert s1==ii['sha1']
    rows.append(row); print('CANDIDATE='+json.dumps(row,ensure_ascii=False),flush=True)
(OUT/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
