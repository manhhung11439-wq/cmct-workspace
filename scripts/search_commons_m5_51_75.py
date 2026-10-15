import json, time
from pathlib import Path
import requests
OUT=Path('evidence/m5_t1_51_75_commons'); OUT.mkdir(parents=True,exist_ok=True)
rows={
51:('Gentiana scabra',['dried root rhizome','Gentianae Radix et Rhizoma','medicinal root']),
52:('Taraxacum mongolicum',['dried whole plant root','Herba Taraxaci','medicinal herb']),
53:('Isatis tinctoria',['dried root slices','Radix Isatidis','medicinal root']),
54:('Iris domestica',['dried rhizome slices','Rhizoma Belamcandae','medicinal rhizome']),
55:('Paeonia lactiflora',['unpeeled dried root slices','Radix Paeoniae Rubra','red peony root']),
56:('Lycium chinense',['dried root bark','Lycii Cortex','root bark medicinal']),
57:('Artemisia annua',['dried aerial herb','Artemisiae Annuae Herba','medicinal herb dried']),
58:('Andrographis paniculata',['dried aerial herb','Andrographis Herba','medicinal dried herb']),
59:('Callisia fragrans',['harvested stems leaves','dried stems leaves','medicinal material']),
60:('Pseuderanthemum palatiferum',['harvested mature leaves','dried leaves','medicinal leaves']),
61:('Helicteres hirsuta',['dried stems leaves','roasted medicinal herb','harvested branches leaves']),
62:('Paederia lanuginosa',['harvested fresh leaves','medicinal leaves']),
63:('Ampelopsis cantoniensis',['dried stems leaves','medicinal dried herb','vine tea dried']),
64:('Hedyotis capitellata',['dried stems leaves','medicinal dried herb']),
65:('Crinum latifolium',['dried sliced leaves','roasted leaves medicinal','medicinal leaf']),
66:('Portulaca oleracea',['dried whole plant','medicinal dried herb','harvested whole herb']),
67:('Sphagneticola calendulacea',['dried whole plant','medicinal dried herb','harvested whole herb']),
68:('Phyllostachys nigra',['dried young bamboo leaves','bamboo leaf medicinal','harvested leaves']),
69:('Lophatherum gracile',['dried whole herb','Lophatheri Herba','medicinal dried herb']),
70:('Sophora flavescens',['dried root slices','Sophorae Flavescentis Radix','medicinal root']),
71:('Dictamnus dasycarpus',['dried root bark','Dictamni Cortex','medicinal root bark']),
72:('Fraxinus rhynchophylla',['dried bark pieces','Fraxini Cortex','medicinal bark']),
73:('Viola yedoensis',['dried whole herb','Violae Herba','medicinal dried herb']),
74:('Isatis tinctoria',['dried leaves cut','Isatidis Folium','medicinal dried leaf']),
75:('Strobilanthes cusia',['Indigo Naturalis powder','Qing Dai medicinal powder','fermented indigo lime powder']),
}
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/1.2 systematic processed-medicinal-material search'
api='https://commons.wikimedia.org/w/api.php'
processed=['dried','dry','radix','rhizoma','cortex','folium','herba','powder','medicinal','medicine','slice','bark','root','leaf','leaves','harvest','tea','indigo']
bad=['flowering plant','living plant','habitus','herbarium','pressed specimen','botanical illustration']
allout={}
for rid,(taxon,roles) in rows.items():
    seen={}; qlog=[]
    for role in roles:
        term=f'"{taxon}" {role}'
        params={'action':'query','generator':'search','gsrsearch':term,'gsrnamespace':6,'gsrlimit':18,
                'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','iiurlwidth':900,
                'format':'json','formatversion':2}
        data=None
        for attempt in range(8):
            r=s.get(api,params=params,timeout=60)
            if r.status_code in (429,500,502,503,504):
                time.sleep(int(r.headers.get('Retry-After') or min(45,3*(attempt+1)))); continue
            r.raise_for_status(); data=r.json(); break
        if data is None: continue
        pages=data.get('query',{}).get('pages',[]); qlog.append({'term':term,'count':len(pages)})
        for p in pages:
            ii=(p.get('imageinfo') or [{}])[0]; em=ii.get('extmetadata') or {}
            def val(k):
                v=em.get(k) or {}; return v.get('value') if isinstance(v,dict) else v
            title=p.get('title') or ''
            seen[title]={'title':title,'pageid':p.get('pageid'),'url':ii.get('url'),'thumburl':ii.get('thumburl'),
                'width':ii.get('width'),'height':ii.get('height'),'size':ii.get('size'),'sha1':ii.get('sha1'),
                'license':val('LicenseShortName'),'license_url':val('LicenseUrl'),'artist':val('Artist'),
                'credit':val('Credit'),'description':val('ImageDescription'),'object_name':val('ObjectName'),
                'categories':val('Categories')}
        time.sleep(.7)
    def score(x):
        blob=' '.join(str(x.get(k) or '') for k in ['title','description','object_name','categories']).lower()
        sc=0
        if taxon.lower() in blob: sc+=8
        sc+=sum(2 for z in processed if z in blob)
        lic=(x.get('license') or '').lower()
        if any(z in lic for z in ['cc0','cc by','public domain','pd-','no restrictions']): sc+=4
        if x.get('sha1') and x.get('url'): sc+=2
        sc-=sum(5 for z in bad if z in blob)
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x['title']))
    for x in vals: x['score']=score(x)
    allout[str(rid)]={'taxon':taxon,'roles':roles,'queries':qlog,'candidates':vals[:25]}
    print(rid,taxon,'unique',len(vals),'top',[(v['score'],v['title'],v.get('license')) for v in vals[:6]],flush=True)
(OUT/'candidates.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding='utf-8')

