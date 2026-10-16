import json,hashlib,pathlib,requests,time
from PIL import Image
OUT=pathlib.Path("evidence/m5_t1_082_houttuynia"); OUT.mkdir(parents=True,exist_ok=True)
TITLE="File:Houttuynia cordata DokudamiSaigon.jpg"
api="https://commons.wikimedia.org/w/api.php"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/7.0 exact M5 acquisition"
params={"action":"query","format":"json","prop":"imageinfo","titles":TITLE,"iiprop":"url|size|sha1|extmetadata"}
r=s.get(api,params=params,timeout=120); r.raise_for_status(); data=r.json()
(OUT/"commons_api.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
page=next(iter(data["query"]["pages"].values())); ii=page["imageinfo"][0]
url=ii["url"]
last=None
for i in range(8):
    rr=s.get(url,timeout=180); last=rr
    if rr.status_code in (429,500,502,503,504):
        time.sleep(min(60,2*(2**i))); continue
    rr.raise_for_status(); break
b=rr.content
p=OUT/"m5_082_Houttuynia_cordata_DokudamiSaigon.jpg"; p.write_bytes(b)
sha1=hashlib.sha1(b).hexdigest(); sha256=hashlib.sha256(b).hexdigest()
im=Image.open(p); im.load()
ext=ii.get("extmetadata",{})
def val(k): return ext.get(k,{}).get("value")
manifest={
 "id":82,"commons_title":TITLE,"original_url":url,"bytes":len(b),"width":im.width,"height":im.height,
 "api_width":ii.get("width"),"api_height":ii.get("height"),"api_sha1":ii.get("sha1"),"sha1":sha1,"sha256":sha256,
 "api_sha1_match":sha1==ii.get("sha1"),
 "description":val("ImageDescription"),"artist":val("Artist"),"credit":val("Credit"),
 "license_short":val("LicenseShortName"),"license_url":val("LicenseUrl"),"usage_terms":val("UsageTerms"),
 "categories":val("Categories"),"date_time_original":val("DateTimeOriginal")
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_082_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
