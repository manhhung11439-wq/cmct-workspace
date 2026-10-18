import json,hashlib,pathlib,time,requests
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_108_blumea"); OUT.mkdir(parents=True,exist_ok=True)
OBS=288432654; PHOTO=518709951; TARGET="Blumea lacera"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/34.2 exact Blumea lacera harvested aerial-part acquisition"
def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()

o=get(f"https://api.inaturalist.org/v1/observations/{OBS}").json()["results"][0]
assert o["quality_grade"]=="research",o["quality_grade"]
assert o["taxon"]["name"]==TARGET,(o["taxon"]["name"],TARGET)
photo=next(p for p in o.get("photos",[]) if p["id"]==PHOTO)
lic=(photo.get("license_code") or "").lower()
assert lic in {"cc0","cc-by","cc-by-sa"},lic
u=photo["url"]
orig=u.replace("square.","original.") if "square." in u else u.replace("/square.","/original.")
b=get(orig).content
ext=pathlib.Path(orig.split("?")[0]).suffix or ".jpg"
fn=OUT/f"m5_108_Blumea_lacera_harvested_aerial_part{ext}"; fn.write_bytes(b)
im=Image.open(fn); im.load(); s1,s256=hh(b)
rec={
 "id":108,"target":"Cải Trời / Blumea lacera (Burm.f.) DC.",
 "observation_id":OBS,"observation_quality_grade":o.get("quality_grade"),
 "taxon_id":o["taxon"]["id"],"taxon_name":o["taxon"]["name"],"taxon_rank":o["taxon"].get("rank"),
 "observed_on":o.get("observed_on"),"place_guess":o.get("place_guess"),"description":o.get("description"),
 "photo_id":PHOTO,"photo_license":lic,"photo_attribution":photo.get("attribution"),
 "photo_url":photo.get("url"),"original_url":orig,
 "file":str(fn),"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,
 "sha1":s1,"sha256":s256,
 "manuscript_role":"§108.5 explicitly permits fresh use. Visual target is a detached aerial flowering stem/branch laid flat beside a ruler. Caption must state fresh harvested aerial material and must not claim washing/drying.",
 "controller_status":"ORIGINAL_ACQUIRED; visual lock required before promotion"
}
(OUT/"observation.json").write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"manifest.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(rec,ensure_ascii=False),flush=True)
