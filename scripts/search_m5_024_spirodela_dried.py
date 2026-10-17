import json,time,requests,pathlib,re,html
OUT=pathlib.Path('evidence/m5_t1_024_spirodela_search'); OUT.mkdir(parents=True,exist_ok=True)
queries=['"Spirodela polyrhiza" dried','"Spirodela polyrrhiza" dried','"Herba Spirodelae"','"Fu Ping" Spirodela']
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/21.2 Spirodela dried-herb Commons search'
def get(params):
    last=None
    for i in range(8):
        r=s.get('https://commons.wikimedia.org/w/api.php',params=params,timeout=180); last=r
        if r.status_code in (429,500,502,503,504): time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r.json()
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get('value','')
    return re.sub(r'<[^>]+>','',html.unescape(str(v))).strip()
out={}
for q in queries:
    data=get({'action':'query','format':'json','generator':'search','gsrsearch':q,'gsrnamespace':6,'gsrlimit':50,'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata'})
    rows=[]
    for p in (data.get('query',{}).get('pages',{}) or {}).values():
        ii=(p.get('imageinfo') or [{}])[0]; m=ii.get('extmetadata',{})
        rows.append({'title':p.get('title'),'pageid':p.get('pageid'),'url':ii.get('url'),'width':ii.get('width'),'height':ii.get('height'),'sha1':ii.get('sha1'),
                     'description':clean(m.get('ImageDescription','')),'author':clean(m.get('Artist','')),'license':clean(m.get('LicenseShortName','')),
                     'license_url':clean(m.get('LicenseUrl','')),'categories':clean(m.get('Categories',''))})
    out[q]=rows
    print('QUERY',q,'RESULTS',len(rows),flush=True)
    for x in rows[:20]: print(json.dumps(x,ensure_ascii=False),flush=True)
(OUT/'search_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
