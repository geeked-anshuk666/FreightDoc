#!/usr/bin/env python3
"""Deterministic release/CI checks for FreightDoc (standard library only)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CheckFailure(RuntimeError):
    pass


def read(path: Path) -> str:
    if not path.is_file():
        raise CheckFailure(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [name for name in result.stdout.decode("utf-8", "replace").split("\0") if name]


def check_repository_hygiene() -> None:
    files = tracked_files()
    forbidden = re.compile(r"(?:^|/)\.env(?:\.(?:local|production|development|test))?$")
    bad_env = [name for name in files if forbidden.search(name)]
    require(not bad_env, "tracked runtime environment file(s): " + ", ".join(bad_env))

    secret = re.compile(
        r"(?:gsk_[A-Za-z0-9_-]{16,}|npg_[A-Za-z0-9_-]{16,}|"
        r"sk_(?:live|test)_[A-Za-z0-9_-]{16,}|BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY)"
    )
    hits: list[str] = []
    for name in files:
        try:
            text = (ROOT / name).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if secret.search(text):
            hits.append(name)
    require(not hits, "potential secret token in tracked file(s): " + ", ".join(hits))


def check_pwa() -> None:
    index = read(ROOT / "frontend" / "index.html")
    read(ROOT / "frontend" / "public" / "offline.html")

    vite = read(ROOT / "frontend" / "vite.config.js")
    # vite-plugin-pwa injects the manifest link into the generated index.
    require('rel="manifest"' in index or "VitePWA" in vite,
            "frontend must link or generate a web manifest")
    require("manifest:" in vite, "vite PWA config must define a manifest")
    for token in ("navigateFallbackDenylist", "api", "sign-in", "sign-up"):
        require(token in vite, f"vite PWA config missing denylist entry: {token}")

    dist = ROOT / "frontend" / "dist"
    if not dist.is_dir():
        return
    for filename in ("index.html", "manifest.webmanifest", "sw.js", "offline.html"):
        require((dist / filename).is_file() and (dist / filename).stat().st_size > 0,
                f"missing or empty frontend/dist/{filename}")
    manifest = json.loads(read(dist / "manifest.webmanifest"))
    for key in ("name", "short_name", "start_url", "scope", "display", "icons"):
        require(manifest.get(key), f"PWA manifest missing {key}")
    require(manifest["display"] in {"standalone", "fullscreen", "minimal-ui"},
            "PWA manifest display must be installable")
    sw = read(dist / "sw.js")
    for token in ("denylist", "api", "sign-in", "sign-up"):
        require(token in sw, f"service worker missing navigation denylist token: {token}")


def check_deployment_descriptors() -> None:
    docker = read(ROOT / "backend" / "Dockerfile")
    for token in ("USER freightdoc", "HEALTHCHECK", "PORT", "uvicorn app.main:app"):
        require(token in docker, f"Dockerfile missing production safeguard: {token}")

    render = read(ROOT / "render.yaml")
    for token in ("plan: free", "dockerContext: ./backend", "dockerfilePath: ./backend/Dockerfile", "healthCheckPath: /health"):
        require(token in render, f"render.yaml missing deployment setting: {token}")
    require("sync: false" in render, "render.yaml must keep secrets dashboard-managed")

    vercel = json.loads(read(ROOT / "frontend" / "vercel.json"))
    rewrites = vercel.get("rewrites", [])
    require(any(item.get("destination") == "/index.html" for item in rewrites),
            "vercel.json must provide SPA fallback to /index.html")
    headers = json.dumps(vercel.get("headers", []))
    for token in ("X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy"):
        require(token in headers, f"vercel.json missing security header: {token}")


def check_api_contract_docs() -> None:
    docs = read(ROOT / "docs" / "api_reference.md")
    for route in ("/health", "/api/country-pairs", "/api/classify", "/api/generate", "/api/validate", "/api/full-pipeline"):
        require(route in docs, f"API contract documentation missing route: {route}")


def main() -> int:
    checks = (
        ("repository hygiene", check_repository_hygiene),
        ("PWA artifacts", check_pwa),
        ("deployment descriptors", check_deployment_descriptors),
        ("API contract docs", check_api_contract_docs),
    )
    failures: list[str] = []
    for label, check in checks:
        try:
            check()
        except (CheckFailure, json.JSONDecodeError) as exc:
            failures.append(f"{label}: {exc}")
        else:
            print(f"PASS {label}")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
