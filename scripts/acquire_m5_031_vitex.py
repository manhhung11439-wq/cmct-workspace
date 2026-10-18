import json,hashlib,pathlib,time,requests,html,re
from PIL import Image
OUT=pathlib.Path('evidence/m5_t1_031_vitex_negundo'); OUT.mkdir(parents=True,exist_ok=True)
TITLE='File:Vitex negundo-1-bsi-yercaud-salem-India.JPG'
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/35.2 Vitex negundo harvested leafy branch acquisition'
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
q=get('https://commons.wikimedia.org/w/api.php',{
 'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','titles':TITLE
}).json()
p=next(iter(q['query']['pages'].values())); ii=p['imageinfo'][0]; meta=ii.get('extmetadata',{})
b=get(ii['url']).content
out=OUT/'m5_031_Vitex_negundo_harvested_leafy_branch.JPG'; out.write_bytes(b)
im=Image.open(out); im.load(); s1,s256=hh(b)
rec={
 'id':31,'target':'Ngũ Trảo / Vitex negundo L. / leaves (fresh permitted)',
 'title':TITLE,'pageid':p.get('pageid'),'canonical_title':p.get('title'),
 'description':clean(meta.get('ImageDescription','')),'author':clean(meta.get('Artist','')),
 'credit':clean(meta.get('Credit','')),'license_short':clean(meta.get('LicenseShortName','')),
 'license_url':clean(meta.get('LicenseUrl','')),'usage_terms':clean(meta.get('UsageTerms','')),
 'categories':clean(meta.get('Categories','')),'original_url':ii['url'],
 'api_sha1':ii.get('sha1'),'local_sha1':s1,'local_sha256':s256,
 'bytes':len(b),'width':im.width,'height':im.height,'format':im.format,'file':str(out),
 'controller_role':'Visually detached leafy flowering branch laid flat on white sheet; exact species; manuscript §31.1 used part includes leaves and §31.5 permits fresh use. Caption must be conservative: fresh leaves on a cut/harvested branch, no claim of washing/drying.'
}
assert s1==ii.get('sha1'),(s1,ii.get('sha1'))
(OUT/'manifest.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
print('MANIFEST='+json.dumps(rec,ensure_ascii=False),flush=True)
