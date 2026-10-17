import json,hashlib,pathlib,time,requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_039_scleromitrion_inat"); OUT.mkdir(parents=True,exist_ok=True)
OBS_ID=288802896; PHOTO_ID=519396129; TAXON_ID=1404885; TAXON_NAME="Scleromitrion diffusum"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/32.0 exact Scleromitrion diffusum harvested whole-plant acquisition"
def get(u):
    last=None
    for i in range(8):
        r=s.get(u,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
obsj=get(f"https://api.inaturalist.org/v1/observations/{OBS_ID}").json()
(OUT/"observation.json").write_text(json.dumps(obsj,ensure_ascii=False,indent=2),encoding="utf-8")
res=obsj["results"][0]
assert res["taxon"]["id"]==TAXON_ID,(res["taxon"]["id"],TAXON_ID)
assert res["taxon"]["name"]==TAXON_NAME,(res["taxon"]["name"],TAXON_NAME)
photo=next(p for p in res["photos"] if p["id"]==PHOTO_ID)
lic=photo.get("license_code")
if lic not in ("cc-by","cc0","cc-by-sa"): raise RuntimeError(f"Non-reusable photo license: {lic}")
url=photo["url"].replace("/square.","/original.")
b=get(url).content
p=OUT/"m5_039_Scleromitrion_diffusum_uprooted_whole_plant.jpg"; p.write_bytes(b)
im=Image.open(p); im.load(); s1,s256=hh(b)
man={
 "id":39,"target":"Bạch Hoa Xà Thiệt Thảo / Scleromitrion diffusum (Willd.) R.J.Wang",
 "observation_id":OBS_ID,"quality_grade":res.get("quality_grade"),
 "taxon_id":res["taxon"]["id"],"taxon_name":res["taxon"]["name"],"taxon_rank":res["taxon"].get("rank"),
 "observed_on":res.get("observed_on"),"place_guess":res.get("place_guess"),
 "photo_id":PHOTO_ID,"license":lic,"attribution":photo.get("attribution"),
 "original_url":url,"file":str(p),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,
 "sha1":s1,"sha256":s256,
 "manuscript_role":"§39.5: harvest whole plant in summer-autumn, wash, use fresh or dry. Visual target: entire uprooted plant with roots, fresh state, before washing.",
 "controller_status":"ORIGINAL_ACQUIRED; VISUAL LOCK REQUIRED BEFORE PROMOTION"
}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
