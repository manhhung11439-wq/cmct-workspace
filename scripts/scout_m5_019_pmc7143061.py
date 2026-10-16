import io,json,hashlib,pathlib,time,zipfile,xml.etree.ElementTree as ET
import requests
from PIL import Image
OUT=pathlib.Path('evidence/m5_t1_019_pmc7143061'); OUT.mkdir(parents=True,exist_ok=True)
PMC='PMC7143061'; XL='{http://www.w3.org/1999/xlink}href'
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/7.0 exact Cryptotympana atrata exuviae figure scout'
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504): time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
xr=get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML'); xb=xr.content
(OUT/'fulltext.xml').write_bytes(xb); root=ET.fromstring(xb)
article_text=' '.join(''.join(root.itertext()).split())
figs=[]
for fig in root.iter('fig'):
    lab=' '.join(''.join(fig.find('label').itertext()).split()) if fig.find('label') is not None else ''
    cap=fig.find('caption'); ct=' '.join(''.join(cap.itertext()).split()) if cap is not None else ''
    hrefs=[]
    for g in fig.iter('graphic'):
        h=g.attrib.get(XL) or g.attrib.get('href') or ''
        if h: hrefs.append(h)
    figs.append({'id':fig.attrib.get('id',''),'label':lab,'caption':ct,'graphics':hrefs})
print('FIGS='+json.dumps(figs,ensure_ascii=False),flush=True)
sr=get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/supplementaryFiles?inlineImages=true'); zb=sr.content
(OUT/'inline_images.zip').write_bytes(zb)
if not zipfile.is_zipfile(io.BytesIO(zb)): raise RuntimeError('inlineImages did not return ZIP')
imgs=[]
with zipfile.ZipFile(io.BytesIO(zb)) as z:
    names=z.namelist(); print('NAMES='+json.dumps(names,ensure_ascii=False),flush=True)
    for fi,f in enumerate(figs,1):
        stems=[pathlib.PurePosixPath(h).name.lower().rsplit('.',1)[0] for h in f['graphics']]
        for n in names:
            bn=pathlib.PurePosixPath(n).name.lower()
            if stems and not any(st and st in bn for st in stems): continue
            try:
                data=z.read(n); im=Image.open(io.BytesIO(data)); im.load()
            except: continue
            if im.width<150 or im.height<100: continue
            ext=(im.format or 'JPEG').lower().replace('jpeg','jpg')
            p=OUT/f'fig_{fi:02d}_{len(imgs)+1:02d}.{ext}'; p.write_bytes(data)
            s1,s256=hh(data)
            imgs.append({'figure_index':fi,'label':f['label'],'caption':f['caption'],'archive_member':n,'file':str(p),'bytes':len(data),'width':im.width,'height':im.height,'format':im.format,'sha1':s1,'sha256':s256})
            break
man={'pmc':PMC,'xml_url':xr.url,'xml_sha1':hh(xb)[0],'xml_sha256':hh(xb)[1],'figures':figs,'images':imgs,'article_text_has_cc_by':('Creative Commons Attribution' in article_text or 'CC BY' in article_text),'article_text_tail':article_text[-3000:]}
(OUT/'manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf-8')
print('MANIFEST='+json.dumps(man,ensure_ascii=False),flush=True)
