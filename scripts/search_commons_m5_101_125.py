import json,time
from pathlib import Path
import requests
OUT=Path('evidence/m5_t1_101_125_commons');OUT.mkdir(parents=True,exist_ok=True)
rows={
101:('Paris polyphylla',['dried rhizome slices','Paridis Rhizoma','medicinal rhizome']),
102:('Premna serratifolia',['harvested leaves','dried leaves medicinal','root bark medicinal']),
103:('Tiliacora triandra',['harvested fresh leaves','medicinal leaves']),
104:('Platostoma palustre',['dried aerial whole herb','harvested medicinal herb']),
105:('Peperomia pellucida',['fresh whole plant harvested','medicinal fresh herb']),
106:('Glinus oppositifolius',['dried whole plant','harvested medicinal herb']),
107:('Hibiscus rosa-sinensis',['harvested flowers leaves','dried medicinal flower leaf']),
108:('Blumea lacera',['dried aerial whole plant','harvested medicinal herb']),
109:('Terminalia catappa',['dried leaves medicinal','harvested leaf']),
110:('Mangifera indica',['dried leaves medicinal','harvested leaf']),
111:('Annona muricata',['dried leaves medicinal','harvested leaf']),
112:('Pteris multifida',['dried whole herb','harvested medicinal herb']),
113:('Peristrophe bivalvis',['harvested leaves stems','dried medicinal herb']),
114:('Gynura procumbens',['harvested fresh leaves young stems','medicinal leaves']),
115:('Clerodendrum chinense',['dried root leaves flowers medicinal','harvested medicinal material']),
116:('Acanthus ilicifolius',['dried root medicinal','harvested root']),
117:('Commelina communis',['dried aerial herb','harvested medicinal herb']),
118:('Barleria lupulina',['harvested leaves young twigs','medicinal leaves']),
119:('Breynia fruticosa',['dried leaves twigs roots medicinal','harvested material']),
120:('Ludwigia hyssopifolia',['dried aerial whole plant','harvested medicinal herb']),
121:('Phyllanthus acidus',['dried leaves medicinal','dried fruit medicinal','harvested medicinal material']),
122:('Paramignya trimera',['dried root stem slices','harvested medicinal root stem']),
123:('Scutellaria barbata',['dried whole plant flowering','Scutellariae Barbatae Herba','medicinal dried herb']),
124:('Clinacanthus nutans',['harvested leaves young twigs','dried medicinal leaves']),
125:('Scoparia dulcis',['dried whole plant','Herba Scopariae','medicinal dried herb'])
}
s=requests.Session();s.headers['User-Agent']='CMCT-image-audit/1.2 systematic processed-medicinal-material search';api='https://commons.wikimedia.org/w/api.php'
good=['dried','dry','radix','rhizoma','cortex','folium','flos','herba','medicinal','medicine','slice','root','leaf','leaves','harvest','whole herb','stems','twigs']
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
            if r.status_code in (429,500,502,503,504):time.sleep(int(r.headers.get('Retry-After') or min(45,3*(a+1))));continue
            r.raise_for_status();data=r.json();break
        if data is None:continue
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
        if taxon.lower() in blob:sc+=8
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

