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

probe("GET",url+"?t=456", origin=True)
try:
    req=urllib.request.Request(url,headers={"Accept":"application/json","Origin":"https://ryanehinkle.github.io","User-Agent":"Mozilla/5.0 Chrome/155.0.0.0"},method="GET")
    with urllib.request.urlopen(req,timeout=15) as response:
        live=json.load(response)
    if live.get("data") and isinstance(live["data"].get("entries"),list):
        # Write the unchanged collection to verify a browser-origin PUT.
        probe("PUT",url,{"name":"ryanehinkle-mc-banner-tracker","data":live["data"]},origin=True)
        probe("GET",url,origin=True)
except Exception as error:
    print("Browser write test unavailable:",repr(error))
