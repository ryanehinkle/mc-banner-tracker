#!/usr/bin/env python3
"""Provision public no-login storage and keep a repository backup of its contents."""
import json
import os
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "storage.json"
BACKUP = ROOT / "banners.json"
API = "https://superjsonblob.com/api/jsonBlob"


def request(method, url, payload=None):
    headers = {"Accept": "application/json", "User-Agent": "MCBannerTracker-GitHubActions/1.0"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    data = json.dumps(payload).encode() if payload is not None else None
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers, method=method), timeout=25) as response:
        return json.loads(response.read().decode()), dict(response.headers)


def validate(items):
    if not isinstance(items, list):
        raise ValueError("Shared collection must be an array")
    entries = []
    for e in items:
        if not isinstance(e, dict):
            continue
        if isinstance(e.get("url"), str) and isinstance(e.get("name"), str) and isinstance(e.get("id"), str):
            entries.append({k: e[k] for k in ("id", "url", "name", "done", "created") if k in e})
    return entries


if CONFIG.exists():
    config = json.loads(CONFIG.read_text())
    url = config["url"]
    if not url.startswith(API + "/"):
        raise ValueError("Unexpected storage URL")
    response, _ = request("GET", url)
    items = validate(response["entries"])
    output = json.dumps(items, indent=2, ensure_ascii=False) + "\n"
    if not BACKUP.exists() or BACKUP.read_text() != output:
        BACKUP.write_text(output)
        print("Updated repo backup with", len(items), "banners")
    else:
        print("Backup already up-to-date")
else:
    existing = []
    if BACKUP.exists():
        existing = validate(json.loads(BACKUP.read_text()))
    created, headers = request("POST", API, {"entries": existing})
    identifier = created.get("id") or headers.get("Location", "").strip("/").split("/")[-1]
    if not isinstance(identifier, str) or not identifier:
        raise ValueError("Storage API did not return an ID")
    url = API + "/" + identifier
    check, _ = request("GET", url)
    if not isinstance(check, dict) or not isinstance(check.get("entries"), list):
        raise ValueError("Storage could not be verified")
    CONFIG.write_text(json.dumps({"url": url}, indent=2) + "\n")
    print("Created shared public store", url)
