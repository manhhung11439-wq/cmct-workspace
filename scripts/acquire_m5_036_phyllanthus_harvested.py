import json,hashlib,pathlib,time,requests,html,re
from PIL import Image
OUT=pathlib.Path('evidence/m5_t1_036_phyllanthus_harvested'); OUT.mkdir(parents=True,exist_ok=True)
TITLE='File:Phyllanthus urinaria.JPG'
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/20.3 Phyllanthus urinaria harvested whole-plant acquisition'
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
q=get('https://commons.wikimedia.org/w/api.php',{'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','titles':TITLE}).json()
p=next(iter(q['query']['pages'].values())); ii=p['imageinfo'][0]; m=ii.get('extmetadata',{})
b=get(ii['url']).content; fn=OUT/'m5_036_Phyllanthus_urinaria_harvested_whole_plant.jpg'; fn.write_bytes(b)
im=Image.open(fn); im.load(); s1,s256=hh(b); assert s1==ii.get('sha1'),(s1,ii.get('sha1'))
rec={'id':36,'target':'Diệp Hạ Châu / Phyllanthus urinaria L.','title':TITLE,'canonical_title':p.get('title'),'pageid':p.get('pageid'),
'original_url':ii['url'],'api_sha1':ii.get('sha1'),'local_sha1':s1,'local_sha256':s256,'bytes':len(b),'width':im.width,'height':im.height,'format':im.format,'file':str(fn),
'description':clean(m.get('ImageDescription','')),'author':clean(m.get('Artist','')),'credit':clean(m.get('Credit','')),'license_short':clean(m.get('LicenseShortName','')),'license_url':clean(m.get('LicenseUrl','')),'usage_terms':clean(m.get('UsageTerms','')),'copyrighted':clean(m.get('Copyrighted','')),'categories':clean(m.get('Categories','')),'date_time_original':clean(m.get('DateTimeOriginal','')),
'manuscript_role':'§36.5: Thu hái toàn cây vào mùa hè–thu, rửa sạch, dùng tươi hoặc phơi/sấy khô. Candidate visually shows entire uprooted plant with root laid on neutral surface.',
'controller_status':'ORIGINAL_ACQUIRED; VISUAL LOCK REQUIRED BEFORE PROMOTION'}
(OUT/'manifest.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
print('MANIFEST='+json.dumps(rec,ensure_ascii=False),flush=True)
