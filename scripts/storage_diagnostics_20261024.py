#!/usr/bin/env python3
import json,urllib.request, urllib.parse,urllib.error,datetime,time
def test(method,url,data=None,extra=None):
 h={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/155.0.0.0","Accept":"*/*"}
 if extra:h.update(extra)
 req=urllib.request.Request(url,method=method,headers=h,data=data)
 try:
  with urllib.request.urlopen(req,timeout=13) as r:
   print(method,url[:130],r.status,repr(r.read(320).decode("utf-8","replace")),dict(r.headers).get("Access-Control-Allow-Origin"))
 except urllib.error.HTTPError as e: print(method,url[:130],e.code,repr(e.read(220).decode("utf-8","replace")),dict(e.headers).get("Access-Control-Allow-Origin"))
 except Exception as e: print(method,url[:130],"EXCEPTION",str(e))
key="ryanehinkle-banner-probe-20261024"
value="abc123-hello"
q=urllib.parse.quote(value,safe="")
test("GET","https://api.keyval.org/get/"+key)
test("GET","https://api.keyval.org/set/"+key+"/"+q)
test("GET","https://api.keyval.org/get/"+key)
test("GET","https://api.keyval.org/get/"+key,extra={"Origin":"https://ryanehinkle.github.io"})
test("OPTIONS","https://api.keyval.org/set/"+key+"/"+q,extra={"Origin":"https://ryanehinkle.github.io","Access-Control-Request-Method":"GET"})
test("GET","https://mantledb.sh/v2/ryanehinkle-mc-probe-20261024/health",extra={"Origin":"https://ryanehinkle.github.io"})
test("OPTIONS","https://mantledb.sh/v2/ryanehinkle-mc-probe-20261024/health",extra={"Origin":"https://ryanehinkle.github.io","Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"content-type"})
