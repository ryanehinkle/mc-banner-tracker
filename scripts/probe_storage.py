#!/usr/bin/env python3
import json, urllib.request, urllib.error
def probe(method,url, data=None, origin=None):
    headers={"Accept":"application/json","User-Agent":"BannerTrackerDiagnostics/1.0"}
    if data is not None: headers["Content-Type"]="application/json"
    if origin:
        headers.update({"Origin":"https://ryanehinkle.github.io","Access-Control-Request-Method":"PUT","Access-Control-Request-Headers":"content-type"})
    req=urllib.request.Request(url,data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=12) as r:
            raw=r.read(600).decode(errors="replace")
            result=(r.status,raw,dict(r.headers))
    except urllib.error.HTTPError as e:
        result=(e.code,e.read(400).decode(errors="replace"),dict(e.headers))
    except Exception as e:result=("ERROR",str(e),{})
    print(method,url,"status:",result[0],"body:",result[1][:240], "access:",result[2].get("Access-Control-Allow-Origin"), "methods:",result[2].get("Access-Control-Allow-Methods"))
    return result
url="https://api.restful-api.dev/objects/ff808181a09d98f701a16f65f4220128"
probe("GET",url)
probe("GET",url+"?t=123")
probe("OPTIONS",url,origin=True)
endpoint="https://api.jsonstorage.net/v1/json"
created=probe("POST",endpoint,{"entries":[{"id":"probe","name":"test","url":"https://minecraft.tools/en/banner.php?color_id_0=13"}]})
try:
    info=json.loads(created[1]); key=info.get("uri") or info.get("url")
    if key:
        probe("GET",key)
        probe("OPTIONS",key,origin=True)
        probe("PUT",key,{"entries":[{"id":"probe","name":"updated","url":"https://minecraft.tools/en/banner.php?color_id_0=13"}]})
        probe("GET",key)
except Exception as e:print("jsonstorage parse failed",str(e))
