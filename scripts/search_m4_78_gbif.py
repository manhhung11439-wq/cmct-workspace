import json, requests, time
from pathlib import Path
OUT=Path("evidence/m4_78_exact_natural"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/1.9 exact-variety natural-photo search"
names=[
 "Mesostemma dichotomum var. lanceolatum",
 "Stellaria dichotoma var. lanceolata",
 "Stellaria dichotoma f. lanceolata",
 "Stellaria gypsophiloides var. lanceolata",
]
matches=[]; candidates=[]
for name in names:
    mr=s.get("https://api.gbif.org/v1/species/match",params={"name":name},timeout=60); mr.raise_for_status(); m=mr.json()
    matches.append({"query":name,"match":m})
    keys=[]
    for k in ["usageKey","acceptedUsageKey"]:
        if m.get(k) and m.get(k) not in keys: keys.append(m.get(k))
    queries=[{"scientificName":name}]+[{"taxon_key":k} for k in keys]
    for q0 in queries:
        params={"media_type":"StillImage","limit":300}
        if "taxon_key" in q0: params["taxon_key"]=q0["taxon_key"]
        else: params["scientific_name"]=q0["scientificName"]
        r=s.get("https://api.gbif.org/v1/occurrence/search",params=params,timeout=90); r.raise_for_status(); d=r.json()
        for rec in d.get("results",[]):
            sci=(rec.get("scientificName") or "")
            acc=(rec.get("acceptedScientificName") or "")
            if "lanceolat" not in (sci+" "+acc).lower(): continue
            for media in rec.get("media") or []:
                ident=media.get("identifier") or media.get("references")
                if not ident: continue
                lic=media.get("license") or rec.get("license")
                basis=rec.get("basisOfRecord")
                candidates.append({
                  "source":"GBIF","query":q0,"gbifKey":rec.get("key"),"scientificName":sci,
                  "acceptedScientificName":acc,"taxonRank":rec.get("taxonRank"),"basisOfRecord":basis,
                  "natural_role": basis in ("HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"),
                  "identifiedBy":rec.get("identifiedBy"),"recordedBy":rec.get("recordedBy"),
                  "country":rec.get("country"),"locality":rec.get("locality"),"eventDate":rec.get("eventDate"),
                  "occurrenceStatus":rec.get("occurrenceStatus"),"issue":rec.get("issues"),
                  "mediaIdentifier":ident,"mediaReferences":media.get("references"),"mediaTitle":media.get("title"),
                  "mediaDescription":media.get("description"),"creator":media.get("creator"),"license":lic,
                  "rightsHolder":media.get("rightsHolder") or rec.get("rightsHolder"),
                  "occurrenceID":rec.get("occurrenceID"),"datasetTitle":rec.get("datasetTitle")
                })
        time.sleep(.1)

# iNaturalist exact-name / synonym search.
inat_taxa=[]
inat_candidates=[]
for name in names:
    tr=s.get("https://api.inaturalist.org/v1/taxa",params={"q":name,"per_page":50},timeout=60)
    if tr.ok:
        for t in tr.json().get("results",[]):
            blob=" ".join([str(t.get("name") or ""),str(t.get("preferred_common_name") or ""),
                           " ".join(t.get("matched_term") or [] if isinstance(t.get("matched_term"),list) else [str(t.get("matched_term") or "")])])
            if "lanceolat" not in blob.lower(): continue
            inat_taxa.append({"query":name,"id":t.get("id"),"name":t.get("name"),"rank":t.get("rank"),"matched_term":t.get("matched_term")})
# dedup taxon ids
seen_tax=set()
for t in inat_taxa:
    tid=t.get("id")
    if not tid or tid in seen_tax: continue
    seen_tax.add(tid)
    page=1
    while page<=5:
        rr=s.get("https://api.inaturalist.org/v1/observations",params={
            "taxon_id":tid,"photos":"true","quality_grade":"research,needs_id","per_page":200,"page":page,"order_by":"observed_on"
        },timeout=90)
        if not rr.ok: break
        js=rr.json(); results=js.get("results",[])
        for o in results:
            tx=o.get("taxon") or {}
            txname=tx.get("name") or ""
            if "lanceolat" not in txname.lower() and "lanceolat" not in str(t.get("name") or "").lower(): continue
            for p in o.get("photos") or []:
                lic=p.get("license_code")
                url=p.get("url")
                if not url: continue
                original=url.replace("/square.","/original.").replace("/small.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
                inat_candidates.append({
                    "source":"iNaturalist","taxon_id":tid,"taxon_name":txname,"taxon_rank":tx.get("rank"),
                    "observation_id":o.get("id"),"quality_grade":o.get("quality_grade"),
                    "observed_on":o.get("observed_on_string"),"place_guess":o.get("place_guess"),
                    "user_login":(o.get("user") or {}).get("login"),"photo_id":p.get("id"),
                    "license":lic,"attribution":p.get("attribution"),"url":url,"original_url":original,
                    "natural_role":True
                })
        if len(results)<200: break
        page+=1
        time.sleep(.2)

# dedup GBIF media and rank strict natural reusable candidates
seen={}; 
for x in candidates: seen[x["mediaIdentifier"]]=x
candidates=list(seen.values())
strict_gbif=[x for x in candidates if x.get("natural_role") and str(x.get("license") or "").lower() not in ("","all rights reserved")]
strict_inat=[x for x in inat_candidates if str(x.get("license") or "").lower() in ("cc0","cc-by","cc-by-sa","cc_by","cc_by_sa")]

(OUT/"gbif_matches.json").write_text(json.dumps(matches,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"gbif_exact_media_candidates.json").write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"gbif_strict_natural_reusable.json").write_text(json.dumps(strict_gbif,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"inat_exact_taxa.json").write_text(json.dumps(inat_taxa,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"inat_exact_photo_candidates.json").write_text(json.dumps(inat_candidates,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"inat_strict_natural_reusable.json").write_text(json.dumps(strict_inat,ensure_ascii=False,indent=2),encoding="utf-8")
print("GBIF_MATCHES",json.dumps(matches,ensure_ascii=False))
print("GBIF_ALL_EXACT",len(candidates),"GBIF_STRICT_NATURAL_REUSABLE",len(strict_gbif))
for x in strict_gbif[:100]: print("GBIF_STRICT",json.dumps(x,ensure_ascii=False))
print("INAT_TAXA",json.dumps(inat_taxa,ensure_ascii=False))
print("INAT_ALL_EXACT_PHOTOS",len(inat_candidates),"INAT_STRICT_NATURAL_REUSABLE",len(strict_inat))
for x in strict_inat[:100]: print("INAT_STRICT",json.dumps(x,ensure_ascii=False))
