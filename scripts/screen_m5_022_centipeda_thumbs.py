import json,pathlib,time,requests,html,re
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path('evidence/m5_t1_022_centipeda_thumbs'); OUT.mkdir(parents=True,exist_ok=True)
CAT='Category:Centipeda minima'
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/21.3 Centipeda visual-screen'
def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=120,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(30,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get('value','')
    return re.sub(r'<[^>]+>','',html.unescape(str(v))).strip()
cm=get('https://commons.wikimedia.org/w/api.php',{'action':'query','format':'json','list':'categorymembers','cmtitle':CAT,'cmnamespace':6,'cmlimit':50}).json()
titles=[x['title'] for x in cm['query']['categorymembers']]
rows=[]; cards=[]
for idx,title in enumerate(titles,1):
    q=get('https://commons.wikimedia.org/w/api.php',{'action':'query','format':'json','prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','iiurlwidth':700,'titles':title}).json()
    p=next(iter(q['query']['pages'].values())); ii=p['imageinfo'][0]; m=ii.get('extmetadata',{})
    tu=ii.get('thumburl') or ii.get('url')
    b=get(tu).content; fn=OUT/f'thumb_{idx:02d}.jpg'; fn.write_bytes(b)
    im=Image.open(fn).convert('RGB')
    rows.append({'idx':idx,'title':title,'pageid':p.get('pageid'),'original_url':ii.get('url'),'thumb_url':tu,'api_sha1':ii.get('sha1'),
                 'width':ii.get('width'),'height':ii.get('height'),'description':clean(m.get('ImageDescription','')),
                 'author':clean(m.get('Artist','')),'license':clean(m.get('LicenseShortName','')),'license_url':clean(m.get('LicenseUrl','')),
                 'categories':clean(m.get('Categories','')),'thumb_file':str(fn)})
    # card
    canvas=Image.new('RGB',(760,620),'white')
    fit=ImageOps.contain(im,(720,500)); canvas.paste(fit,((760-fit.width)//2,20))
    dr=ImageDraw.Draw(canvas); dr.text((15,535),f"{idx:02d} {title[:70]}",fill='black'); dr.text((15,565),f"{clean(m.get('LicenseShortName',''))} | {clean(m.get('Artist',''))[:70]}",fill='black')
    cards.append(canvas)
# contact
cols=2; rowsn=(len(cards)+cols-1)//cols; sheet=Image.new('RGB',(cols*760,rowsn*620),'white')
for i,c in enumerate(cards): sheet.paste(c,((i%cols)*760,(i//cols)*620))
sheet.save(OUT/'contact.jpg',quality=90)
(OUT/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('COUNT',len(rows),'CONTACT',OUT/'contact.jpg',flush=True)
