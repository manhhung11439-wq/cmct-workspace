import json, re
from pathlib import Path
from io import BytesIO

import requests
from PIL import Image, ImageDraw

OUT = Path("evidence/m5_19_inat_permissive")
OUT.mkdir(parents=True, exist_ok=True)
TAXON_ID = 319989
LICENSES = {"cc0", "cc-by", "cc-by-sa"}
TERMS = ["exuvia", "molt", "molting", "shell", "exoskeleton", "nymph", "cicada shell"]

s = requests.Session()
s.headers["User-Agent"] = "CMCT-image-audit/1.0"
records = {}
counts = {}

def add_obs(ob, matched_term):
    tax = ob.get("taxon") or {}
    if tax.get("id") != TAXON_ID:
        return
    for ph in ob.get("photos") or []:
        lic = (ph.get("license_code") or "").lower()
        if lic not in LICENSES:
            continue
        pid = ph.get("id")
        url = ph.get("url") or ""
        if not pid or not url:
            continue
        records[pid] = {
            "photo_id": pid,
            "license": lic,
            "attribution": ph.get("attribution"),
            "original_dimensions": ph.get("original_dimensions"),
            "obs_id": ob.get("id"),
            "obs_uri": ob.get("uri"),
            "observed_on": ob.get("observed_on"),
            "quality_grade": ob.get("quality_grade"),
            "description": ob.get("description") or "",
            "tags": ob.get("tags") or [],
            "matched_term": matched_term,
            "large_url": url.replace("/square.", "/large."),
            "original_url": url.replace("/square.", "/original."),
            "taxon_name": tax.get("name"),
        }

for term in TERMS:
    params = {
        "taxon_id": TAXON_ID, "photos": "true", "per_page": 200, "page": 1,
        "q": term, "order_by": "created_at", "order": "desc"
    }
    r = s.get("https://api.inaturalist.org/v1/observations", params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    counts[term] = data.get("total_results", 0)
    for ob in data.get("results", []):
        add_obs(ob, term)

keyword = re.compile(r"exuv|molt|shell|exoskel|nymph", re.I)
for page in range(1, 16):
    params = {
        "taxon_id": TAXON_ID, "photos": "true", "per_page": 200, "page": page,
        "order_by": "created_at", "order": "desc"
    }
    r = s.get("https://api.inaturalist.org/v1/observations", params=params, timeout=60)
    r.raise_for_status()
    for ob in r.json().get("results", []):
        blob = " ".join([ob.get("description") or "", *(ob.get("tags") or [])])
        if keyword.search(blob):
            add_obs(ob, "metadata-scan")

recs = sorted(records.values(), key=lambda x: (x["license"], str(x["photo_id"])))
(OUT / "query_counts.json").write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "candidates.json").write_text(json.dumps(recs, ensure_ascii=False, indent=2), encoding="utf-8")

thumbs = []
for rec in recs[:200]:
    try:
        rr = s.get(rec["large_url"], timeout=60)
        rr.raise_for_status()
        im = Image.open(BytesIO(rr.content)).convert("RGB")
        im.thumbnail((220, 160))
        canvas = Image.new("RGB", (240, 205), "white")
        canvas.paste(im, ((240-im.width)//2, 4+(160-im.height)//2))
        d = ImageDraw.Draw(canvas)
        label = f'pid {rec["photo_id"]} | {rec["license"]}\nobs {rec["obs_id"]} | {rec["matched_term"]}'
        d.multiline_text((5, 168), label, fill="black", spacing=2)
        thumbs.append(canvas)
    except Exception as e:
        rec["thumb_error"] = str(e)

for si in range(0, len(thumbs), 20):
    batch = thumbs[si:si+20]
    sheet = Image.new("RGB", (240*4, 205*5), "white")
    for j, im in enumerate(batch):
        sheet.paste(im, ((j % 4)*240, (j // 4)*205))
    sheet.save(OUT / f"contact_{si//20+1:02d}.jpg", quality=90)

print("QUERY_COUNTS", json.dumps(counts, ensure_ascii=False))
print("PERMISSIVE_CANDIDATES", len(recs))
for rec in recs:
    print(json.dumps(rec, ensure_ascii=False))
