#!/usr/bin/env python3
"""Maintain the banner tracker public store with atomic writes and GitHub backups.

GitHub Pages hosts only the frontend. MantleDB is an unclaimed, intentionally
public-write namespace. GitHub Actions keeps a versioned backup in banners.json.
"""
import datetime as dt
import json
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "storage.json"
BACKUP = ROOT / "banners.json"
STATUS = ROOT / "storage-status.json"
NEW_URL = "https://mantledb.sh/v2/ryanehinkle-mcbanners-20261024-q7x3f2/shared"
TOPIC = "rh-mcbanners-q7x3f2-20261024"


def call(method, url, payload=None, extra_headers=None):
    headers = {
        "User-Agent": "mc-banner-tracker-backup/2",
        "Accept": "application/json",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if extra_headers:
        headers.update(extra_headers)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, method=method, headers=headers, data=data)
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read().decode("utf-8").strip()
        return (json.loads(raw) if raw else {}), dict(response.headers)


def get_if_exists(url):
    try:
        return call("GET", url)[0]
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def valid(e):
    return isinstance(e, dict) and all(isinstance(e.get(k), str) for k in ("id", "url", "name"))


def import_old():
    old = {}
    if BACKUP.exists():
        for entry in json.loads(BACKUP.read_text()):
            if valid(entry):
                old[entry["id"]] = entry

    if CONFIG.exists():
        config = json.loads(CONFIG.read_text())
        url = config.get("url", "")
        if url.startswith("https://api.restful-api.dev/objects/"):
            try:
                result, _ = call("GET", url)
                for entry in result.get("data", {}).get("entries", []):
                    if valid(entry):
                        old[entry["id"]] = entry
            except Exception as exc:
                print("Old provider unavailable; using GitHub backup:", str(exc))
    return old


current = get_if_exists(NEW_URL)
if current is None:
    imported = import_old()
    call("POST", NEW_URL, {"entries": imported})
    current = get_if_exists(NEW_URL)
    if current is None or not isinstance(current.get("entries"), dict):
        raise RuntimeError("New shared store did not preserve initialized banners")
    print("Initialized new shared collection with", len(imported), "banners")
else:
    if not isinstance(current.get("entries"), dict):
        raise RuntimeError("Unexpected storage structure; will not overwrite data")
    print("Using existing collection with", len(current["entries"]), "banners")

# A tiny daily heartbeat avoids the 30-day inactivity expiry for free namespaces.
now = dt.datetime.now(dt.timezone.utc)
if now.hour == 0 and 10 <= now.minute < 50:
    call("PATCH", NEW_URL, {"_heartbeat": now.date().isoformat()})
    current = get_if_exists(NEW_URL)

# Validate actual browser CORS, including the PATCH preflight.
_, cors_headers = call(
    "OPTIONS", NEW_URL, extra_headers={
        "Origin": "https://ryanehinkle.github.io",
        "Access-Control-Request-Method": "PATCH",
        "Access-Control-Request-Headers": "content-type",
    })
origin = cors_headers.get("Access-Control-Allow-Origin", "")
methods = cors_headers.get("Access-Control-Allow-Methods", "")
allowed = cors_headers.get("Access-Control-Allow-Headers", "")
checks = {
    "origin": origin in ("*", "https://ryanehinkle.github.io"),
    "patch": "PATCH" in methods.upper(),
    "content_type": "content-type" in allowed.lower() or "*" in allowed,
}
if not all(checks.values()):
    raise RuntimeError("Browser PATCH access not verified: " + str(checks))
STATUS.write_text(json.dumps(checks, indent=2) + "\n")
CONFIG.write_text(json.dumps({"url": NEW_URL, "realtime_topic": TOPIC}, indent=2) + "\n")
print("CORS verified:", checks)

saved = [e for e in current["entries"].values() if valid(e)]
saved.sort(key=lambda e: e.get("created", 0), reverse=True)
output = json.dumps(saved, ensure_ascii=False, indent=2) + "\n"
if not BACKUP.exists() or BACKUP.read_text() != output:
    BACKUP.write_text(output)
    print("Updated repo backup with", len(saved), "banners")
else:
    print("Backup is current")
