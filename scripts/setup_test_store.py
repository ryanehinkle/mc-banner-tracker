#!/usr/bin/env python3
"""Create isolated, empty public store for two-device browser smoke test."""
import json, os, pathlib, urllib.request
ns="ryanehinkle-mc-smoke-"+os.environ.get("GITHUB_RUN_ID","local")+"-banners"
url=f"https://mantledb.sh/v2/{ns}/shared"
topic=f"rh-mc-smoke-{os.environ.get('GITHUB_RUN_ID','local')}"
headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"Mozilla/5.0 (X11; Linux x86_64) Chrome/155.0.0.0","Origin":"https://ryanehinkle.github.io"}
data=json.dumps({"entries":{}}).encode()
req=urllib.request.Request(url,data=data,method="POST",headers=headers)
with urllib.request.urlopen(req,timeout=30) as r:
 print("Provisioned isolated test store:",r.status)
pathlib.Path("storage.json").write_text(json.dumps({"url":url,"realtime_topic":topic}))
