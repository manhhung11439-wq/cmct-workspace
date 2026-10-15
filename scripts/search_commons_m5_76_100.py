import json,time
from pathlib import Path
import requests
OUT=Path('evidence/m5_t1_76_100_commons');OUT.mkdir(parents=True,exist_ok=True)
rows={
76:('Patrinia scabiosifolia',['dried whole herb','Herba Patriniae','medicinal dried herb']),
77:('Lithospermum erythrorhizon',['dried root slices','Arnebiae Lithospermi Radix','medicinal root']),
79:('Picrorhiza scrophulariiflora',['dried rhizome','Picrorhizae Rhizoma','medicinal rhizome']),
80:('Cynanchum atratum',['dried root rhizome','Cynanchi Atrati Radix et Rhizoma','medicinal root']),
81:('Centella asiatica',['harvested whole plant','dried whole herb','medicinal herb']),
82:('Houttuynia cordata',['dried aerial herb','harvested herb medicinal','Houttuyniae Herba']),
83:('Ageratum conyzoides',['dried aerial herb flowering','harvested medicinal herb']),
84:('Oroxylum indicum',['dried stem bark','dried mature winged seeds','medicinal bark seed']),
85:('Euphorbia thymifolia',['dried whole herb','harvested whole plant medicinal']),
86:('Catharanthus roseus',['dried whole plant','dried root medicinal','harvested medicinal material']),
87:('Gymnanthemum amygdalinum',['harvested mature leaves','dried leaves medicinal']),
88:('Jasminum subtriplinerve',['dried stems leaves','roasted dried stems leaves','medicinal vine herb']),
89:('Excoecaria cochinchinensis',['dried leaves young twigs','roasted medicinal leaves']),
90:('Sauropus androgynus',['fresh harvested leaves','dried root medicinal']),
91:('Nelumbo nucifera',['dried leaf strips','Nelumbinis Folium','lotus leaf medicinal dried']),
92:('Eleusine indica',['dried whole plant','harvested whole herb','medicinal herb']),
93:('Bidens pilosa',['dried aerial herb','harvested medicinal herb']),
94:('Pulsatilla chinensis',['dried root slices','Pulsatillae Radix','medicinal root']),
95:('Sophora tonkinensis',['dried root rhizome','Sophorae Tonkinensis Radix et Rhizoma','medicinal root']),
96:('Calvatia',['dried puffball fruiting body','Lasiosphaera medicinal','Puff-ball medicinal dried']),
97:('Lobelia chinensis',['dried whole herb','Lobeliae Chinensis Herba','medicinal dried herb']),
100:('Kalanchoe pinnata',['detached fresh leaves harvested','medicinal fresh leaf'])
}
s=requests.Session();s.headers['User-Agent']='CMCT-image-audit/1.2 systematic processed-medicinal-material search';api='https://commons.wikimedia.org/w/api.php'
good=['dried','dry','radix','rhizoma','cortex','folium','herba','medicinal','medicine','slice','bark','root','leaf','leaves','harvest','seed','fruiting body']
bad=['flowering plant','living plant','habitus','herbarium','pressed specimen','botanical illustration']
allout={}
for rid,(taxon,roles) in rows.items():
    seen={};qlog=[]
    for role in roles:
        term=f'"{taxon}" {role}'
        params={'action':'query','generator':'search','gsrsearch':term,'gsrnamespace':6,'gsrlimit':20,'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','iiurlwidth':900,'format':'json','formatversion':2}
        data=None
        for a in range(8):
            r=s.get(api,params=params,timeout=60)
            if r.status_code in (429,500,502,503,504): time.sleep(int(r.headers.get('Retry-After') or min(45,3*(a+1))));continue
            r.raise_for_status();data=r.json();break
        if data is None: continue
        pages=data.get('query',{}).get('pages',[]);qlog.append({'term':term,'count':len(pages)})
        for p in pages:
            ii=(p.get('imageinfo') or [{}])[0];em=ii.get('extmetadata') or {}
            def val(k):
                v=em.get(k) or {};return v.get('value') if isinstance(v,dict) else v
            title=p.get('title') or ''
            seen[title]={'title':title,'pageid':p.get('pageid'),'url':ii.get('url'),'thumburl':ii.get('thumburl'),'width':ii.get('width'),'height':ii.get('height'),'size':ii.get('size'),'sha1':ii.get('sha1'),'license':val('LicenseShortName'),'license_url':val('LicenseUrl'),'artist':val('Artist'),'credit':val('Credit'),'description':val('ImageDescription'),'object_name':val('ObjectName'),'categories':val('Categories')}
        time.sleep(.7)
    def score(x):
        blob=' '.join(str(x.get(k) or '') for k in ['title','description','object_name','categories']).lower();sc=0
        if taxon.lower() in blob: sc+=8
        sc+=sum(2 for z in good if z in blob)
        lic=(x.get('license') or '').lower()
        if any(z in lic for z in ['cc0','cc by','public domain','pd-','no restrictions']):sc+=4
        if x.get('sha1') and x.get('url'):sc+=2
        sc-=sum(5 for z in bad if z in blob)
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x['title']))
    for x in vals:x['score']=score(x)
    allout[str(rid)]={'taxon':taxon,'roles':roles,'queries':qlog,'candidates':vals[:25]}
    print(rid,taxon,'unique',len(vals),'top',[(v['score'],v['title'],v.get('license')) for v in vals[:6]],flush=True)
(OUT/'candidates.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding='utf-8')

