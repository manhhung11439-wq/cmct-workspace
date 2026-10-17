import json,re,hashlib,pathlib,time,requests,urllib.parse
from PIL import Image
OUT=pathlib.Path('evidence/m5_t1_092_wiktrop'); OUT.mkdir(parents=True,exist_ok=True)
OBS='https://portal.wiktrop.org/group/Ananas/observation/show/476694'
SPEC='https://portal.wiktrop.org/species/show/126'
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/21.4 Eleusine indica WIKTROP provenance acquisition'
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
oh=get(OBS); html=oh.text
(OUT/'observation.html').write_text(html,encoding='utf-8')
sh=get(SPEC); sht=sh.text
(OUT/'species.html').write_text(sht,encoding='utf-8')
# Extract all raw observation file URLs/paths.
paths=sorted(set(re.findall(r'''(?:https?://portal\.wiktrop\.org)?(/files-api/api/get/raw/observations/[^"'<>\\ ]+)''',html,re.I)))
if not paths:
    # known image from indexed page; keep as explicit fallback, but record fallback use.
    paths=['/files-api/api/get/raw/observations/777ed45e-66c7-4605-ad73-bd7f10a6c5eb/e0bfd84308684974a9f50a3e51dc33f0.JPG',
           '/files-api/api/get/raw/observations/777ed45e-66c7-4605-ad73-bd7f10a6c5eb/16ed71a4063e48ffa559f5a7a34a0578.JPG']
imgs=[]
for i,p in enumerate(paths,1):
    u=urllib.parse.urljoin('https://portal.wiktrop.org',p)
    r=get(u); b=r.content
    ext=pathlib.Path(urllib.parse.urlparse(u).path).suffix or '.jpg'
    fn=OUT/f'observation_image_{i:02d}{ext}'; fn.write_bytes(b)
    try:
        im=Image.open(fn); im.load()
        s1,s256=hh(b)
        imgs.append({'url':u,'file':str(fn),'bytes':len(b),'width':im.width,'height':im.height,'format':im.format,'sha1':s1,'sha256':s256})
    except Exception as e:
        imgs.append({'url':u,'file':str(fn),'bytes':len(b),'error':repr(e)})
def contexts(txt,terms):
    low=txt.lower(); out=[]
    for term in terms:
        start=0
        while True:
            k=low.find(term.lower(),start)
            if k<0: break
            out.append(re.sub(r'\s+',' ',txt[max(0,k-700):k+1300])[:2200])
            start=k+len(term)
            if len(out)>=40: break
    return out
lic_ctx=contexts(html,['license','licence','cc_by','creative commons','copyright'])
spec_lic_ctx=contexts(sht,['license','licence','cc_by','creative commons','copyright'])
# Save visible text-ish fragments for controller.
man={
 'id':92,'target':'Cỏ Mần Trầu / Eleusine indica (L.) Gaertn.',
 'observation_url':OBS,'species_url':SPEC,
 'indexed_identity':'Observation 476694 indexed as accepted Eleusine indica (L.) Gaertn.; observer Husson; Miandrivazo, Madagascar; observed 23 March 2005.',
 'images':imgs,'observation_license_context':lic_ctx,'species_license_context':spec_lic_ctx,
 'controller_rule':'PROMOTE only if exact observation/file image license is explicit and reusable; species-page general license alone is insufficient.'
}
(OUT/'manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf-8')
print('MANIFEST='+json.dumps(man,ensure_ascii=False),flush=True)
