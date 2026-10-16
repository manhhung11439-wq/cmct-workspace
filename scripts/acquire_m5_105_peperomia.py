import requests,pathlib,json,hashlib,time,tarfile,io,re
from xml.etree import ElementTree as ET
OUT=pathlib.Path("evidence/m5_t1_105_peperomia"); OUT.mkdir(parents=True,exist_ok=True)
pmcid="PMC11637809"
oa=f"https://pmc.ncbi.nlm.nih.gov/utils/oa/oa.fcgi?id={pmcid}"
s=requests.Session(); s.headers["User-Agent"]="CMCT-image-audit/5.0 PMC OA package Peperomia"
def get(u):
  last=None
  for i in range(8):
    r=s.get(u,timeout=120,allow_redirects=True); last=r
    if r.status_code in (429,500,502,503,504):
      time.sleep(min(30,2*(2**i))); continue
    r.raise_for_status(); return r
  last.raise_for_status()
xml=get(oa).content
(OUT/"oa_response.xml").write_bytes(xml)
root=ET.fromstring(xml)
links=root.findall(".//link")
tgz=None
for link in links:
  if link.attrib.get("format")=="tgz":
    tgz=link.attrib.get("href"); break
if not tgz: raise RuntimeError("PMC OA tgz link not found")
if tgz.startswith("ftp://"):
  tgz="https://"+tgz[len("ftp://"):]
r=get(tgz); data=r.content
if len(data)<10000: raise RuntimeError("unexpected small OA package")
pkg=OUT/"pmc11637809_oa.tar.gz"; pkg.write_bytes(data)
p_sha1=hashlib.sha1(data).hexdigest(); p_sha256=hashlib.sha256(data).hexdigest()
extract=OUT/"oa"; extract.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(data),mode="r:gz") as tf:
  tf.extractall(extract)
files=[]
for p in extract.rglob("*"):
  if p.is_file():
    files.append({"path":str(p.relative_to(extract)),"bytes":p.stat().st_size})
# Find likely original figure 1 raster files by names and dimensions later.
cands=[x for x in files if re.search(r"(fig|f1|figure)",x["path"],re.I) and re.search(r"\.(jpe?g|png|tif?f)$",x["path"],re.I)]
manifest={"id":105,"pmcid":pmcid,"doi":"10.4014/jmb.2406.06025",
 "title":"Peperomia pellucida's Ingredients, Antioxidant Properties, and Safe Usage as Food and Herbal Medicine",
 "identity":"Peperomia pellucida (L.) Kunth",
 "caption":"Fig. 1. Botanical characteristics of Peperomia pellucida (L.) Kunth. (A) Wild-type P. pellucida. (B) Leaf shape of the vegetable. (C) The whole body of the vegetable. The trees were harvested in Can Tho City, Viet Nam. The collected samples were washed and damaged parts were removed and dried at room temperature and shade conditions.",
 "license":"CC BY","oa_endpoint":oa,"oa_tgz_url":tgz,
 "oa_package":{"file":str(pkg),"bytes":len(data),"sha1":p_sha1,"sha256":p_sha256},
 "candidate_figure_files":cands,"all_file_count":len(files)}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("M5_105_MANIFEST="+json.dumps(manifest,ensure_ascii=False),flush=True)
