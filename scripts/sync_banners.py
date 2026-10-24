#!/usr/bin/env python3
"""Provision tokenless shared banner storage and periodically back it up to GitHub."""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "storage.json"
BACKUP = ROOT / "banners.json"
STATUS = ROOT / "storage-status.json"
BASE = "https://api.restful-api.dev/objects"
NAME = "ryanehinkle-mc-banner-tracker"


def call(method, url, payload=None, headers=None):
    req_headers = {
        "User-Agent": "MCBannerTracker-GitHubActions/1.0",
        "Accept": "application/json",
    }
    if payload is not None:
        req_headers["Content-Type"] = "application/json"
    if headers:
        req_headers.update(headers)
    data = json.dumps(payload).encode() if payload is not None else None
    with urllib.request.urlopen(
        urllib.request.Request(url, data=data, headers=req_headers, method=method),
        timeout=25,
    ) as response:
        content = response.read().decode().strip()
        return json.loads(content) if content else {}, dict(response.headers)


def validate(items):
    if not isinstance(items, list):
        raise ValueError("Invalid banner collection: expected list")
    return [
        {key: e[key] for key in ("id", "url", "name", "done", "created") if key in e}
        for e in items
        if isinstance(e, dict)
        and isinstance(e.get("id"), str)
        and isinstance(e.get("url"), str)
        and isinstance(e.get("name"), str)
    ]


def load_previous():
    if CONFIG.exists():
        config = json.loads(CONFIG.read_text())
        existing_url = config.get("url", "")
        if existing_url.startswith(BASE + "/"):
            return existing_url, []
        if existing_url.startswith("https://superjsonblob.com/api/jsonBlob/"):
            obj, _ = call("GET", existing_url)
            return None, validate(obj.get("entries", []))
    if BACKUP.exists():
        return None, validate(json.loads(BACKUP.read_text()))
    return None, []


url, old_entries = load_previous()
if url is None:
    created, _ = call("POST", BASE, {
        "name": NAME,
        "data": {"entries": old_entries},
    })
    identifier = created.get("id")
    if not identifier:
        raise RuntimeError("Public database did not return an ID")
    url = BASE + "/" + str(identifier)
    # Verify that the document accepts real persistent writes.
    result, _ = call("GET", url)
    if validate(result.get("data", {}).get("entries", [])) != old_entries:
        raise RuntimeError("Created collection could not be read back")
    call("PUT", url, {"name": NAME, "data": {"entries": old_entries}})
    updated, _ = call("GET", url)
    if validate(updated.get("data", {}).get("entries", [])) != old_entries:
        raise RuntimeError("Created collection could not be updated")
    CONFIG.write_text(json.dumps({"url": url}, indent=2) + "\n")
    print("Initialized shared banner storage:", url)

try:
    req_headers = {
        "Origin": "https://ryanehinkle.github.io",
        "Access-Control-Request-Method": "PUT",
        "Access-Control-Request-Headers": "content-type",
    }
    _, headers = call("OPTIONS", url, headers=req_headers)
    allow_origin = headers.get("Access-Control-Allow-Origin", "")
    allow_methods = headers.get("Access-Control-Allow-Methods", "")
    allow_headers = headers.get("Access-Control-Allow-Headers", "")
    status = {
        "origin": allow_origin in ("*", "https://ryanehinkle.github.io"),
        "put": "PUT" in allow_methods.upper(),
        "content_type": "content-type" in allow_headers.lower() or "*" in allow_headers,
    }
except Exception as exc:
    status = {"error": str(exc)}
STATUS.write_text(json.dumps(status, indent=2) + "\n")
print("Browser CORS verification:", status)

record, _ = call("GET", url)
items = validate(record.get("data", {}).get("entries", []))
serialized = json.dumps(items, indent=2, ensure_ascii=False) + "\n"
if not BACKUP.exists() or BACKUP.read_text() != serialized:
    BACKUP.write_text(serialized)
    print("Backed up", len(items), "banners")
else:
    print("Backup is current")
