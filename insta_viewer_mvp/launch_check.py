"""
Pre-launch sanity check script.

Run from the insta_viewer_mvp/ directory:
    python launch_check.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "

errors = 0


def check(label: str, ok: bool, detail: str = "", warn_only: bool = False):
    global errors
    icon = PASS if ok else (WARN if warn_only else FAIL)
    suffix = f"  → {detail}" if detail else ""
    print(f"  {icon}  {label}{suffix}")
    if not ok and not warn_only:
        errors += 1


print("\n=== FollowspyV Launch Check ===\n")

# ------------------------------------------------------------------
# 1. Environment variables
# ------------------------------------------------------------------
print("[1] Environment Variables")
check("RAPIDAPI_KEY set",    bool(os.getenv("RAPIDAPI_KEY")),    "required for story fetching")
check("RAPIDAPI_HOST set",   bool(os.getenv("RAPIDAPI_HOST")),   "required for story fetching")
check(
    "COOKIE_SECRET set",
    bool(os.getenv("COOKIE_SECRET")),
    "using YAML fallback — set a strong secret for production",
    warn_only=True,
)

# ------------------------------------------------------------------
# 2. Required files
# ------------------------------------------------------------------
print("\n[2] Required Files")
required_files = [
    "app.py",
    "config_auth.yaml",
    "requirements.txt",
    ".env",
    ".streamlit/config.toml",
    "services/instagram.py",
    "utils/media_handler.py",
    "utils/rate_limiter.py",
    "utils/logger_helper.py",
    "pages/1_Viewer.py",
    "pages/2_Terms.py",
    "pages/3_Privacy.py",
]
for f in required_files:
    check(f, Path(f).exists())

# ------------------------------------------------------------------
# 3. SQLite rate-limiter DB (writable)
# ------------------------------------------------------------------
print("\n[3] Rate-Limiter Database")
from utils.rate_limiter import RateLimiter, _DB_PATH

db_ok = False
try:
    rl = RateLimiter()
    rl.is_allowed("launch_check_probe")
    db_ok = True
except Exception as exc:
    check("SQLite DB writable", False, str(exc))

if db_ok:
    check("SQLite DB writable", True, str(_DB_PATH))

# ------------------------------------------------------------------
# 4. API connectivity
# ------------------------------------------------------------------
print("\n[4] Third-Party API Connectivity")
import requests

api_key  = os.getenv("RAPIDAPI_KEY", "")
api_host = os.getenv("RAPIDAPI_HOST", "")

if api_key and api_host:
    try:
        resp = requests.get(
            f"https://{api_host}/v1/stories",
            headers={"x-rapidapi-key": api_key, "x-rapidapi-host": api_host},
            params={"username_or_id_or_url": "instagram"},
            timeout=8,
        )
        check(
            f"API responds (HTTP {resp.status_code})",
            resp.status_code in (200, 404),
            "200/404 both confirm auth is working",
        )
    except requests.exceptions.Timeout:
        check("API connectivity", False, "request timed out")
    except requests.exceptions.RequestException as exc:
        check("API connectivity", False, str(exc))
else:
    check("API connectivity", False, "RAPIDAPI_KEY or RAPIDAPI_HOST not set — skipped")

# ------------------------------------------------------------------
# 5. Download payload (media_handler)
# ------------------------------------------------------------------
print("\n[5] Media Download Engine")
from utils.media_handler import download_media_bytes

_TEST_URL = "https://httpbin.org/image/jpeg"
try:
    data = download_media_bytes(_TEST_URL)
    check(
        "download_media_bytes returns bytes",
        isinstance(data, bytes) and len(data) > 0,
        f"{len(data)} bytes fetched from test URL",
    )
except Exception as exc:
    # Network-dependent — treat as warning so CI in restricted envs doesn't block launch
    check("download_media_bytes (network test)", False, str(exc), warn_only=True)

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
print(f"\n{'='*34}")
if errors == 0:
    print(f"  {PASS}  All checks passed. Ready to launch!")
else:
    print(f"  {FAIL}  {errors} check(s) failed. Fix before deploying.")
print()

sys.exit(0 if errors == 0 else 1)
