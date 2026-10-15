import json,time
from pathlib import Path
import requests

OUT=Path('evidence/m5_t1_fresh_harvest_commons'); OUT.mkdir(parents=True,exist_ok=True)
rows={
2:("Perilla frutescens",["fresh leaves","picked leaves","harvested perilla","perilla leaves market"]),
20:("Cymbopogon citratus",["fresh stalks","lemongrass market","harvested lemongrass"]),
52:("Taraxacum mongolicum",["harvested whole plant","fresh herb","picked dandelion"]),
59:("Callisia fragrans",["cut stems leaves","harvested leaves"]),
60:("Pseuderanthemum palatiferum",["fresh leaves","picked leaves"]),
62:("Paederia lanuginosa",["fresh leaves","picked leaves"]),
66:("Portulaca oleracea",["harvested whole plant","fresh purslane bunch","purslane market"]),
67:("Sphagneticola calendulacea",["harvested whole plant","fresh herb"]),
68:("Phyllostachys nigra",["young bamboo leaves","picked bamboo leaves"]),
73:("Viola yedoensis",["harvested whole plant","fresh herb flowering"]),
81:("Centella asiatica",["harvested whole plant","fresh gotu kola bunch","gotu kola market"]),
82:("Houttuynia cordata",["fresh herb bunch","fish mint market","picked leaves stems"]),
83:("Ageratum conyzoides",["harvested aerial parts","fresh herb"]),
85:("Euphorbia thymifolia",["harvested whole plant","fresh herb"]),
90:("Sauropus androgynus",["fresh leaves","picked leaves","leaves market"]),
92:("Eleusine indica",["harvested whole plant","fresh herb roots"]),
93:("Bidens pilosa",["harvested aerial parts","fresh herb"]),
100:("Kalanchoe pinnata",["detached fresh leaves","picked leaves"]),
103:("Tiliacora triandra",["fresh leaves","picked leaves","leaves market"]),
105:("Peperomia pellucida",["harvested whole plant","fresh whole herb","fresh herb bunch"]),
106:("Glinus oppositifolius",["harvested whole plant","fresh herb"]),
114:("Gynura procumbens",["fresh leaves young stems","picked leaves"]),
118:("Barleria lupulina",["fresh leaves young twigs","picked leaves"]),
120:("Ludwigia hyssopifolia",["harvested aerial parts","fresh whole plant"]),
124:("Clinacanthus nutans",["fresh leaves young twigs","picked leaves"]),
}
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/1.3 fresh-harvest medicinal material search'
api='https://commons.wikimedia.org/w/api.php'
good=['harvest','harvested','picked','fresh leaves','leaf','leaves','bunch','bundle','market','stalk','stems','whole plant','herb','vegetable','food','detached']
bad=['flowering plant','growing','in habitat','habitus','herbarium','pressed specimen','botanical illustration','drawing','plate']
allout={}
for rid,(taxon,roles) in rows.items():
    seen={};qlog=[]
    for role in roles:
        term=f'"{taxon}" {role}'
        params={'action':'query','generator':'search','gsrsearch':term,'gsrnamespace':6,'gsrlimit':20,
                'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','iiurlwidth':900,
                'format':'json','formatversion':2}
        data=None
        for attempt in range(8):
            r=s.get(api,params=params,timeout=60)
            if r.status_code==429:
                time.sleep(int(r.headers.get('Retry-After') or min(60,3*(2**attempt)))); continue
            r.raise_for_status();data=r.json();break
        if data is None: continue
        pages=data.get('query',{}).get('pages',[]); qlog.append({'term':term,'count':len(pages)})
        for p in pages:
            ii=(p.get('imageinfo') or [{}])[0]; em=ii.get('extmetadata') or {}
            def val(k):
                v=em.get(k) or {}; return v.get('value') if isinstance(v,dict) else v
            title=p.get('title') or ''
            seen[title]={'title':title,'url':ii.get('url'),'thumburl':ii.get('thumburl'),'sha1':ii.get('sha1'),
                         'width':ii.get('width'),'height':ii.get('height'),'size':ii.get('size'),
                         'license':val('LicenseShortName'),'license_url':val('LicenseUrl'),'artist':val('Artist'),
                         'credit':val('Credit'),'description':val('ImageDescription'),'object_name':val('ObjectName'),
                         'categories':val('Categories')}
        time.sleep(.7)
    def score(x):
        blob=' '.join(str(x.get(k) or '') for k in ['title','description','object_name','categories']).lower()
        sc=0
        if taxon.lower() in blob: sc+=8
        sc+=sum(3 for z in good if z in blob)
        sc-=sum(5 for z in bad if z in blob)
        lic=(x.get('license') or '').lower()
        if any(z in lic for z in ['cc0','cc by','public domain','no restrictions']): sc+=5
        if x.get('url') and x.get('sha1'): sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x['title']))
    for x in vals:x['score']=score(x)
    allout[str(rid)]={'taxon':taxon,'queries':qlog,'candidates':vals[:30]}
    print(rid,taxon,'unique',len(vals),'top',[(v['score'],v['title'],v.get('license')) for v in vals[:8]],flush=True)
(OUT/'candidates.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding='utf-8')
