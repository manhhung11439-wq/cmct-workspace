import json,time,re
from pathlib import Path
import requests
OUT=Path('evidence/m5_t1_chinese_crude_search'); OUT.mkdir(parents=True,exist_ok=True)
rows={
33:("Paeonia suffruticosa",["牡丹皮 中药","Moutan Cortex","Moutan cortex Chinese medicine"]),
40:("Senna tora",["决明子 中药","Cassiae Semen","Senna tora seeds Chinese medicine"]),
42:("Gypsum Fibrosum",["石膏 中药","Gypsum Fibrosum Chinese medicine"]),
43:("Scutellaria baicalensis",["黄芩 中药","Scutellariae Radix","Scutellaria baicalensis root Chinese medicine"]),
44:("Coptis chinensis",["黄连 中药","Coptidis Rhizoma","Coptis chinensis rhizome Chinese medicine"]),
45:("Phellodendron chinense",["黄柏 中药","Phellodendri Cortex Chinese medicine","Phellodendron chinense bark"]),
46:("Lonicera japonica",["金银花 中药","Lonicerae Japonicae Flos","Lonicera japonica dried flower buds"]),
47:("Forsythia suspensa",["连翘 中药","Forsythiae Fructus","Forsythia suspensa dried fruit"]),
48:("Gardenia jasminoides",["栀子 中药","Gardeniae Fructus","Gardenia jasminoides dried fruit"]),
49:("Prunella vulgaris",["夏枯草 中药","Prunellae Spica","Prunella vulgaris Chinese medicine"]),
50:("Phragmites australis",["芦根 中药","Phragmitis Rhizoma","Phragmites dried root Chinese medicine"]),
51:("Gentiana scabra",["龙胆草 中药","Gentianae Radix et Rhizoma","Gentiana dried root Chinese medicine"]),
53:("Isatis indigotica",["板蓝根 中药","Isatidis Radix","Isatis root Chinese medicine"]),
54:("Iris domestica",["射干 中药","Belamcandae Rhizoma","Iris domestica rhizome Chinese medicine"]),
55:("Paeonia lactiflora",["赤芍 中药","Paeoniae Radix Rubra","red peony root Chinese medicine"]),
56:("Lycium chinense",["地骨皮 中药","Lycii Cortex","Lycium root bark Chinese medicine"]),
57:("Artemisia annua",["青蒿 中药","Artemisiae Annuae Herba","Artemisia annua dried herb Chinese medicine"]),
58:("Andrographis paniculata",["穿心莲 中药","Andrographis Herba","Andrographis dried herb Chinese medicine"]),
68:("Phyllostachys nigra",["竹叶 中药","bamboo leaf Chinese medicine","Phyllostachys nigra dried leaf"]),
69:("Lophatherum gracile",["淡竹叶 中药","Lophatheri Herba","Lophatherum gracile Chinese medicine"]),
70:("Sophora flavescens",["苦参 中药","Sophorae Flavescentis Radix","Sophora flavescens root Chinese medicine"]),
71:("Dictamnus dasycarpus",["白鲜皮 中药","Dictamni Cortex","Dictamnus root bark Chinese medicine"]),
72:("Fraxinus chinensis",["秦皮 中药","Fraxini Cortex","Fraxinus chinensis bark Chinese medicine"]),
73:("Viola yedoensis",["紫花地丁 中药","Violae Herba","Viola yedoensis Chinese medicine"]),
74:("Isatis indigotica",["大青叶 中药","Isatidis Folium","Isatis dried leaves Chinese medicine"]),
75:("Indigo Naturalis",["青黛 中药","Indigo Naturalis Chinese medicine","Qing Dai powder Chinese medicine"]),
76:("Patrinia scabiosifolia",["败酱草 中药","Patriniae Herba","Patrinia dried herb Chinese medicine"]),
77:("Lithospermum erythrorhizon",["紫草 中药","Arnebiae Radix","Lithospermum dried root Chinese medicine"]),
78:("Mesostemma dichotomum var. lanceolatum",["银柴胡 中药","Stellariae Radix","Stellaria dichotoma lanceolata root Chinese medicine"]),
79:("Picrorhiza scrophulariiflora",["胡黄连 中药","Picrorhizae Rhizoma","Picrorhiza rhizome Chinese medicine"]),
80:("Cynanchum atratum",["白薇 中药","Cynanchi Atrati Radix et Rhizoma","Cynanchum atratum root Chinese medicine"]),
91:("Nelumbo nucifera",["荷叶 中药","Nelumbinis Folium","Nelumbo nucifera dried leaf Chinese medicine"]),
94:("Pulsatilla chinensis",["白头翁 中药","Pulsatillae Radix","Pulsatilla chinensis dried root Chinese medicine"]),
95:("Sophora tonkinensis",["山豆根 中药","Sophorae Tonkinensis Radix et Rhizoma","Sophora tonkinensis root Chinese medicine"]),
96:("Lasiosphaera fenzlii",["马勃 中药","Lasiosphaera Calvatia Chinese medicine","puffball Chinese medicine dried"]),
97:("Lobelia chinensis",["半边莲 中药","Lobeliae Chinensis Herba","Lobelia chinensis dried herb Chinese medicine"]),
101:("Paris polyphylla",["重楼 中药","Paridis Rhizoma","Paris polyphylla dried rhizome Chinese medicine"]),
123:("Scutellaria barbata",["半枝莲 中药","Scutellariae Barbatae Herba","Scutellaria barbata dried herb Chinese medicine"]),
}
s=requests.Session(); s.headers['User-Agent']='CMCT-image-audit/1.4 exact Chinese crude-drug search'
api='https://commons.wikimedia.org/w/api.php'
good=['中药','chinese medicine','chinese herbal','crude drug','dried','radix','rhizoma','cortex','folium','flos','fructus','semen','spica','herba','root','bark','fruit','seed','powder','药材','生药','漢方','kampo']
bad=['illustration','drawing','plate','herbarium','living','flowering plant','in habitat','tree in','plant in']
allout={}
for rid,(taxon,terms) in rows.items():
    seen={};qlog=[]
    for term in terms:
        params={'action':'query','generator':'search','gsrsearch':term,'gsrnamespace':6,'gsrlimit':30,
                'prop':'imageinfo','iiprop':'url|size|sha1|extmetadata','iiurlwidth':900,
                'format':'json','formatversion':2}
        data=None
        for attempt in range(8):
            r=s.get(api,params=params,timeout=60)
            if r.status_code==429:
                time.sleep(int(r.headers.get('Retry-After') or min(60,3*(2**attempt))));continue
            r.raise_for_status();data=r.json();break
        if data is None:continue
        pages=data.get('query',{}).get('pages',[]);qlog.append({'term':term,'count':len(pages)})
        for p in pages:
            ii=(p.get('imageinfo') or [{}])[0]; em=ii.get('extmetadata') or {}
            def val(k):
                v=em.get(k) or {}; return v.get('value') if isinstance(v,dict) else v
            title=p.get('title') or ''
            seen[title]={'title':title,'pageid':p.get('pageid'),'url':ii.get('url'),'thumburl':ii.get('thumburl'),
              'sha1':ii.get('sha1'),'width':ii.get('width'),'height':ii.get('height'),'size':ii.get('size'),
              'license':val('LicenseShortName'),'license_url':val('LicenseUrl'),'artist':val('Artist'),'credit':val('Credit'),
              'description':val('ImageDescription'),'object_name':val('ObjectName'),'categories':val('Categories')}
        time.sleep(.65)
    def score(x):
        blob=' '.join(str(x.get(k) or '') for k in ['title','description','object_name','categories']).lower()
        sc=0
        if taxon.lower() in blob:sc+=8
        sc+=sum(3 for z in good if z.lower() in blob)
        sc-=sum(6 for z in bad if z in blob)
        lic=(x.get('license') or '').lower()
        if any(z in lic for z in ['cc0','cc by','public domain','free art','no restrictions']):sc+=5
        if x.get('url') and x.get('sha1'):sc+=2
        return sc
    vals=sorted(seen.values(),key=lambda x:(-score(x),x['title']))
    for x in vals:x['score']=score(x)
    allout[str(rid)]={'taxon':taxon,'queries':qlog,'candidates':vals[:30]}
    print(rid,taxon,'unique',len(vals),'top',[(v['score'],v['title'],v.get('license')) for v in vals[:10]],flush=True)
(OUT/'candidates.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding='utf-8')
