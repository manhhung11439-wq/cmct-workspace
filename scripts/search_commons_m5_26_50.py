import json, time
from pathlib import Path
import requests
OUT=Path('evidence/m5_t1_26_50_commons'); OUT.mkdir(parents=True,exist_ok=True)
rows={
26:('Ocimum basilicum',['dried basil leaves','dried herb']),
27:('Ligusticum sinense',['dried root rhizome','medicinal root']),
28:('Allium fistulosum',['white bulb roots','fresh stalk roots']),
29:('Coriandrum sativum',['dried herb medicinal','coriander medicinal material']),
30:('Citrus aurantiifolia',['dried leaves','fresh harvested leaves']),
31:('Vitex negundo',['dried leaves medicinal','harvested leaves']),
32:('Kyllinga nemoralis',['dried whole herb','medicinal herb']),
33:('Paeonia suffruticosa',['dried root bark moutan cortex','Moutan Cortex']),
34:('Solanum procumbens',['dried whole herb','medicinal dried plant']),
35:('Cynara scolymus',['dried leaves','artichoke dried leaf']),
36:('Phyllanthus urinaria',['dried whole herb','medicinal dried plant']),
37:('Gymnema sylvestre',['dried leaves','medicinal leaves']),
38:('Celastrus hindsii',['dried stems leaves','medicinal material']),
39:('Hedyotis diffusa',['dried whole herb','medicinal herb']),
40:('Senna tora',['dried mature seeds','seeds medicinal']),
42:('Gypsum Fibrosum',['medicinal gypsum','crude drug']),
43:('Scutellaria baicalensis',['dried root','Scutellariae Radix']),
44:('Coptis chinensis',['dried rhizome','Coptidis Rhizoma']),
45:('Phellodendron chinense',['dried bark','Phellodendri Cortex']),
46:('Lonicera japonica',['dried flower buds','Lonicerae Japonicae Flos']),
47:('Forsythia suspensa',['dried fruit','Forsythiae Fructus']),
48:('Gardenia jasminoides',['dried mature fruit','Gardeniae Fructus']),
49:('Prunella vulgaris',['dried fruiting spike','Prunellae Spica']),
50:('Phragmites australis',['dried rhizome','Phragmitis Rhizoma']),
}
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/1.1 systematic processed-medicinal-material search'
api='https://commons.wikimedia.org/w/api.php'
processed_terms=['dried','dry','radix','rhizoma','cortex','folium','flos','fructus','semen','spica','herba','medicine','medicinal','crude drug','tea','slice','powder','bark','root','rhizome','seed','fruit','bud','leaf']
live_bad=['flowering plant','living plant','in flower','habitus','herbarium','pressed specimen']
allout={}
for rid,(taxon,roles) in rows.items():
    seen={}; qlog=[]
    for role in roles:
        term=f'"{taxon}" {role}'
        params={'action':'query','generator':'search','gsrsearch':term,'gsrnamespace':6,'gsrlimit':16,
                'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','iiurlwidth':800,
                'format':'json','formatversion':2}
        data=None
        for attempt in range(7):
            r=s.get(api,params=params,timeout=60)
            if r.status_code==429:
                wait=int(r.headers.get('Retry-After') or min(30,4*(attempt+1))); time.sleep(wait); continue
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
        time.sleep(.8)
    def score(x):
        blob=' '.join(str(x.get(k) or '') for k in ['title','description','object_name','categories']).lower()
        sc=sum(2 for z in processed_terms if z in blob)
        if taxon.lower() in blob: sc+=6
        lic=(x.get('license') or '').lower()
        if any(z in lic for z in ['cc0','cc by','public domain','pd-']): sc+=4
        if x.get('sha1') and x.get('url'): sc+=2
        sc-=sum(4 for z in live_bad if z in blob)
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x['title']))
    for x in vals: x['score']=score(x)
    allout[str(rid)]={'taxon':taxon,'roles':roles,'queries':qlog,'candidates':vals[:20]}
    print(rid,taxon,'unique',len(vals),'top',[(v['score'],v['title'],v.get('license')) for v in vals[:5]],flush=True)
(OUT/'candidates.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding='utf-8')
