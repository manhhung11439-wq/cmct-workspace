import json,time,re,html
from pathlib import Path
import requests
OUT=Path("evidence/hanabishi_crude_drugs"); OUT.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="CMCT-image-audit/1.9 Hanabishi crude-drug inventory"
api="https://commons.wikimedia.org/w/api.php"
def get(params):
    for i in range(8):
        r=s.get(api,params=params,timeout=90)
        if r.status_code in (429,500,502,503,504):
            time.sleep(int(r.headers.get("Retry-After") or min(60,2*(2**i))));continue
        r.raise_for_status();return r.json()
    r.raise_for_status()
def clean(v):
    if isinstance(v,dict):v=v.get("value") or ""
    return " ".join(re.sub(r"<[^>]+>"," ",html.unescape(str(v or ""))).split())
titles=[]; cont=None
while True:
    p={"action":"query","list":"usercontribs","ucuser":"Hanabishi","ucnamespace":6,"uclimit":"500","ucprop":"title|timestamp","format":"json","formatversion":2}
    if cont:p["uccontinue"]=cont
    d=get(p); titles.extend(x["title"] for x in d.get("query",{}).get("usercontribs",[]))
    cont=(d.get("continue") or {}).get("uccontinue")
    if not cont:break
titles=list(dict.fromkeys(titles))
print("TOTAL_FILE_TITLES",len(titles),flush=True)
records=[]
for i in range(0,len(titles),50):
    chunk=titles[i:i+50]
    d=get({"action":"query","titles":"|".join(chunk),"prop":"imageinfo",
           "iiprop":"url|sha1|size|extmetadata","format":"json","formatversion":2})
    for p in d.get("query",{}).get("pages",[]):
        ii=(p.get("imageinfo") or [{}])[0];em=ii.get("extmetadata") or {};e=lambda k:clean(em.get(k) or "")
        rec={"title":p.get("title"),"url":ii.get("url"),"sha1":ii.get("sha1"),"size":ii.get("size"),
             "width":ii.get("width"),"height":ii.get("height"),"author":e("Artist"),"credit":e("Credit"),
             "license":e("LicenseShortName"),"license_url":e("LicenseUrl"),"description":e("ImageDescription"),
             "categories":e("Categories"),"object_name":e("ObjectName")}
        blob=" ".join(str(rec.get(k) or "") for k in ("title","description","categories","object_name")).lower()
        keys=["chinese herbal medicines","crude drug","kampo","herbal medicine","生薬","漢方","中薬","中药","药材","藥材"]
        if any(k.lower() in blob for k in keys):
            records.append(rec)
    time.sleep(.3)
records.sort(key=lambda x:x["title"] or "")
(OUT/"hanabishi_crude_drugs.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf-8")
print("MATCHES",len(records),flush=True)
for r in records:
    print("MATCH",r["title"],"|",r["license"],"|",r["description"][:180],"| CATS",r["categories"][:220],flush=True)
