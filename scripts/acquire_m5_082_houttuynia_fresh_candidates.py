import json,hashlib,pathlib,time,requests,html,re
from PIL import Image,ImageOps,ImageDraw
OUT=pathlib.Path("evidence/m5_t1_082_houttuynia_fresh_candidates"); OUT.mkdir(parents=True,exist_ok=True)
TITLES=["File:Rau diếp cá (11340).jpg","File:Uncooked houttuynia cordata.jpg","File:Rau diếp cá (55552).jpg"]
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/33.4 Houttuynia detached aerial candidates"
def get(u,params=None):
    last=None
    for i in range(8):
        r=s.get(u,params=params,timeout=180,allow_redirects=True); last=r
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2*(2**i))); continue
        r.raise_for_status(); return r
    last.raise_for_status()
def clean(v):
    if isinstance(v,dict): v=v.get("value","")
    return re.sub(r"<[^>]+>","",html.unescape(str(v))).strip()
def hh(b): return hashlib.sha1(b).hexdigest(),hashlib.sha256(b).hexdigest()
rows=[]
for idx,title in enumerate(TITLES,1):
    q=get("https://commons.wikimedia.org/w/api.php",{"action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|sha1|extmetadata","titles":title}).json()
    p=next(iter(q["query"]["pages"].values())); ii=p["imageinfo"][0]; meta=ii.get("extmetadata",{})
    b=get(ii["url"]).content; ext=pathlib.Path(ii["url"].split("?")[0]).suffix or ".jpg"
    out=OUT/f"candidate_{idx:02d}{ext}"; out.write_bytes(b)
    im=Image.open(out); im.load(); s1,s256=hh(b)
    row={"title":title,"canonical_title":p.get("title"),"pageid":p.get("pageid"),"original_url":ii["url"],
         "api_sha1":ii.get("sha1"),"local_sha1":s1,"local_sha256":s256,"bytes":len(b),"width":im.width,"height":im.height,"format":im.format,"file":str(out),
         "description":clean(meta.get("ImageDescription","")),"author":clean(meta.get("Artist","")),"credit":clean(meta.get("Credit","")),
         "license_short":clean(meta.get("LicenseShortName","")),"license_url":clean(meta.get("LicenseUrl","")),"usage_terms":clean(meta.get("UsageTerms","")),
         "categories":clean(meta.get("Categories",""))}
    assert s1==ii.get("sha1"),(title,s1,ii.get("sha1")); rows.append(row)
# contact
thumbs=[]
for i,row in enumerate(rows):
    im=Image.open(row["file"]).convert("RGB"); im.thumbnail((500,380))
    c=Image.new("RGB",(520,430),"white"); c.paste(im,((520-im.width)//2,10))
    ImageDraw.Draw(c).text((10,400),f"{i+1}: {row['canonical_title']}",fill="black"); thumbs.append(c)
sheet=Image.new("RGB",(520,len(thumbs)*430),"white")
for i,t in enumerate(thumbs): sheet.paste(t,(0,i*430))
sheet.save(OUT/"contact.jpg",quality=90)
man={"id":82,"target":"Houttuynia cordata aerial whole herb, fresh permitted by §82.5","candidates":rows,"controller_status":"visual audit required; accept only detached aerial stems+leaves matching used part"}
(OUT/"manifest.json").write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding="utf-8")
print("MANIFEST="+json.dumps(man,ensure_ascii=False),flush=True)
