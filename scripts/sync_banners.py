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
API = "https://jsonblob.com/api/jsonBlob"


def request(method, url, payload=None):
    headers = {"Accept": "application/json", "User-Agent": "MCBannerTracker-GitHubActions/1.0"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    data = json.dumps(payload).encode() if payload is not None else None
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers, method=method), timeout=25) as response:
        body = response.read().decode().strip()
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {}
        return parsed, dict(response.headers)


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
        if not url.startswith("https://superjsonblob.com/api/jsonBlob/"):
            raise ValueError("Unexpected storage URL")
        # Upgrade the initial prototype to the browser-compatible, CORS-enabled store.
        old_content, _ = request("GET", url)
        old_items = validate(old_content.get("entries", []))
        migrated, migrated_headers = request("POST", API, {"entries": old_items})
        location = migrated_headers.get("Location", "")
        identifier = migrated.get("id") or location.rstrip("/").split("/")[-1]
        if not identifier:
            raise ValueError("Browser-compatible storage did not provide an ID")
        url = API + "/" + identifier
        verified, _ = request("GET", url)
        if not isinstance(verified.get("entries"), list):
            raise ValueError("New storage was not readable")
        CONFIG.write_text(json.dumps({"url": url}, indent=2) + "\n")
        print("Migrated collection to browser-compatible storage:", url)
    # Check that browsers hosted on GitHub Pages can read and write the shared API.
    cors = {"api": url, "origin_allowed": False, "put_allowed": False, "headers": ""}
    try:
        req = urllib.request.Request(url, method="OPTIONS", headers={
            "Origin": "https://ryanehinkle.github.io",
            "Access-Control-Request-Method": "PUT",
            "Access-Control-Request-Headers": "content-type",
        })
        with urllib.request.urlopen(req, timeout=20) as preflight:
            allow_origin = preflight.headers.get("Access-Control-Allow-Origin", "")
            allow_methods = preflight.headers.get("Access-Control-Allow-Methods", "")
            allow_headers = preflight.headers.get("Access-Control-Allow-Headers", "")
            cors = {
                "api": url,
                "origin_allowed": allow_origin in ("*", "https://ryanehinkle.github.io"),
                "put_allowed": "PUT" in allow_methods.upper(),
                "headers": "content-type" in allow_headers.lower() or "*" in allow_headers,
                "status": preflight.status,
            }
    except Exception as exc:
        cors["error"] = str(exc)
    (ROOT / "storage-status.json").write_text(json.dumps(cors, indent=2) + "\n")
    print("Browser CORS preflight:", cors)
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
