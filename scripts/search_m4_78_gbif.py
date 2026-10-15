import json, requests, time
from pathlib import Path
OUT=Path("evidence/m4_78_exact_natural"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.0"
names=[
 "Mesostemma dichotomum var. lanceolatum",
 "Stellaria dichotoma var. lanceolata",
 "Stellaria dichotoma f. lanceolata",
 "Stellaria gypsophiloides var. lanceolata",
]
matches=[]
candidates=[]
for name in names:
    mr=s.get("https://api.gbif.org/v1/species/match",params={"name":name},timeout=60); mr.raise_for_status(); m=mr.json(); matches.append({"query":name,"match":m})
    keys=[]
    for k in ["usageKey","acceptedUsageKey"]:
        if m.get(k) and m.get(k) not in keys: keys.append(m.get(k))
    queries=[{"scientificName":name}]
    for k in keys: queries.append({"taxon_key":k})
    for q0 in queries:
        params={"media_type":"StillImage","limit":300}
        if "taxon_key" in q0: params["taxon_key"]=q0["taxon_key"]
        else: params["scientific_name"]=q0["scientificName"]
        r=s.get("https://api.gbif.org/v1/occurrence/search",params=params,timeout=90); r.raise_for_status(); d=r.json()
        for rec in d.get("results",[]):
            sci=(rec.get("scientificName") or "")
            acc=(rec.get("acceptedScientificName") or "")
            # strict exact-infraspecific screen: record or accepted name must explicitly carry lanceolat*
            if "lanceolat" not in (sci+" "+acc).lower():
                continue
            for media in rec.get("media") or []:
                ident=media.get("identifier") or media.get("references")
                if not ident: continue
                lic=media.get("license") or rec.get("license")
                candidates.append({
                  "query":q0,"gbifKey":rec.get("key"),"scientificName":sci,"acceptedScientificName":acc,
                  "taxonRank":rec.get("taxonRank"),"basisOfRecord":rec.get("basisOfRecord"),
                  "identifiedBy":rec.get("identifiedBy"),"recordedBy":rec.get("recordedBy"),
                  "country":rec.get("country"),"locality":rec.get("locality"),"eventDate":rec.get("eventDate"),
                  "occurrenceStatus":rec.get("occurrenceStatus"),"issue":rec.get("issues"),
                  "mediaIdentifier":ident,"mediaReferences":media.get("references"),"mediaTitle":media.get("title"),
                  "mediaDescription":media.get("description"),"creator":media.get("creator"),"license":lic,
                  "rightsHolder":media.get("rightsHolder") or rec.get("rightsHolder"),"publisher":rec.get("publishingOrgKey"),
                  "occurrenceID":rec.get("occurrenceID"),"datasetTitle":rec.get("datasetTitle")
                })
        time.sleep(0.1)
# dedup media
seen={}; 
for x in candidates: seen[x["mediaIdentifier"]]=x
candidates=list(seen.values())
(OUT/"gbif_matches.json").write_text(json.dumps(matches,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"gbif_exact_media_candidates.json").write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding="utf-8")
print("MATCHES",json.dumps(matches,ensure_ascii=False))
print("CANDIDATES",len(candidates))
for x in candidates[:100]: print(json.dumps(x,ensure_ascii=False))
