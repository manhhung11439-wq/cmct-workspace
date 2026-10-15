import boto3, json
from botocore import UNSIGNED
from botocore.config import Config
s3=boto3.client("s3", region_name="us-east-1", config=Config(signature_version=UNSIGNED))
def select(key, expr, out):
    resp=s3.select_object_content(
        Bucket="inaturalist-open-data", Key=key,
        ExpressionType="SQL", Expression=expr,
        InputSerialization={"CSV":{"FileHeaderInfo":"USE","FieldDelimiter":"\t","RecordDelimiter":"\n"},"CompressionType":"GZIP"},
        OutputSerialization={"CSV":{"FieldDelimiter":"\t","RecordDelimiter":"\n"}}
    )
    data=b""
    for event in resp["Payload"]:
        if "Records" in event:
            data += event["Records"]["Payload"]
    open(out,"wb").write(data)
    return data.decode("utf-8","replace")
photo=select("photos.csv.gz", "SELECT * FROM S3Object s WHERE s.photo_id = '21995070'", "m5_19_meta/photo_row.tsv")
print("PHOTO",repr(photo))
parts=photo.strip().split("\t")
observer_id=parts[3] if len(parts)>=4 else None
observer=""
if observer_id:
    observer=select("observers.csv.gz", f"SELECT * FROM S3Object s WHERE s.observer_id = '{observer_id}'", "m5_19_meta/observer_row.tsv")
    print("OBSERVER",repr(observer))
open("m5_19_meta/result_summary.json","w",encoding="utf-8").write(json.dumps({"photo_row":photo,"observer_id":observer_id,"observer_row":observer},ensure_ascii=False,indent=2))
