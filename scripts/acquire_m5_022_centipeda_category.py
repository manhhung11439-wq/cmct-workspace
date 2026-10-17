import json,hashlib,pathlib,time,requests,html,re
from PIL import Image
OUT=pathlib.Path('evidence/m5_t1_022_centipeda_category'); OUT.mkdir(parents=True,exist_ok=True)
CAT='Category:Centipeda minima'
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/21.1 Centipeda minima exact-category acquisition'
def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get('value','')
    return re.sub(r'<[^>]+>','',html.unescape(str(v))).strip()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
cm=get('https://commons.wikimedia.org/w/api.php',{'action':'query','format':'json','list':'categorymembers','cmtitle':CAT,'cmnamespace':6,'cmlimit':50}).json()
titles=[x['title'] for x in cm['query']['categorymembers']]
rows=[]
for idx,title in enumerate(titles,1):
    q=get('https://commons.wikimedia.org/w/api.php',{'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','titles':title}).json()
    p=next(iter(q['query']['pages'].values())); ii=p['imageinfo'][0]; m=ii.get('extmetadata',{})
    url=ii['url']; b=get(url).content
    ext=pathlib.Path(url.split('?')[0]).suffix or '.jpg'
    fn=OUT/f'candidate_{idx:02d}{ext}'; fn.write_bytes(b)
    try:
        im=Image.open(fn); im.load()
        wh=(im.width,im.height); fmt=im.format
    except Exception:
        wh=(ii.get('width'),ii.get('height')); fmt=None
    s1,s256=hh(b); assert s1==ii.get('sha1'),(idx,s1,ii.get('sha1'))
    row={'idx':idx,'title':title,'pageid':p.get('pageid'),'original_url':url,'api_sha1':ii.get('sha1'),'local_sha1':s1,'local_sha256':s256,
         'bytes':len(b),'width':wh[0],'height':wh[1],'format':fmt,'file':str(fn),
         'description':clean(m.get('ImageDescription','')),'author':clean(m.get('Artist','')),'credit':clean(m.get('Credit','')),
         'license_short':clean(m.get('LicenseShortName','')),'license_url':clean(m.get('LicenseUrl','')),'usage_terms':clean(m.get('UsageTerms','')),
         'copyrighted':clean(m.get('Copyrighted','')),'categories':clean(m.get('Categories','')),'date_time_original':clean(m.get('DateTimeOriginal',''))}
    rows.append(row); print('CANDIDATE='+json.dumps(row,ensure_ascii=False),flush=True)
(OUT/'manifest.json').write_text(json.dumps({'category':CAT,'count':len(rows),'candidates':rows},ensure_ascii=False,indent=2),encoding='utf-8')
