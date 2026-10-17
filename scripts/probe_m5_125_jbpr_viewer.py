import requests,re,html,json,pathlib
OUT=pathlib.Path("evidence/m5_t1_125_jbpr_probe"); OUT.mkdir(parents=True,exist_ok=True)
urls=[
 "https://jbpr.in/index.php/jbpr/article/view/956/827",
 "https://www.jbpr.in/index.php/jbpr/article/view/956/827",
]
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 CMCT-image-audit/32.0"
res=[]
for u in urls:
    try:
        r=s.get(u,timeout=120,allow_redirects=True)
        txt=r.text
        (OUT/f"viewer_{len(res)+1}.html").write_text(txt,encoding="utf-8",errors="ignore")
        hits=[]
        for pat in [r'pdfUrl\s*=\s*["\']([^"\']+)',r'submissionFileId[^0-9]*(\d+)',r'download-file[^"\'<> ]+']:
            hits += re.findall(pat,txt,re.I)
        res.append({"url":u,"final":r.url,"status":r.status_code,"content_type":r.headers.get("content-type"),"bytes":len(r.content),"hits":hits,"html":txt})
    except Exception as e:
        res.append({"url":u,"error":repr(e)})
print("RESULTS="+json.dumps([{k:v for k,v in x.items() if k!="html"} for x in res],ensure_ascii=False),flush=True)
for i,x in enumerate(res):
    if "html" in x:
        print(f"HTML_{i+1}_BEGIN",flush=True)
        print(x["html"],flush=True)
        print(f"HTML_{i+1}_END",flush=True)
(OUT/"manifest.json").write_text(json.dumps([{k:v for k,v in x.items() if k!="html"} for x in res],ensure_ascii=False,indent=2),encoding="utf-8")
