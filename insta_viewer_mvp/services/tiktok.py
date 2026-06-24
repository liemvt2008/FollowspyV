import json
import os
import re
import urllib.parse

import requests

_UA = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0"

_HEADERS_API = {
    "User-Agent":      _UA,
    "Accept":          "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         "https://www.tiktok.com/",
}

_STORY_API = "https://www.tiktok.com/api/story/item_list/"

_COMMON_PARAMS = {
    "aid":             "1988",
    "app_name":        "tiktok_web",
    "device_platform": "web_pc",
    "region":          "VN",
    "user_is_login":   "false",
}


def _scrape_do_get(url: str, timeout: int = 20) -> requests.Response:
    """Fetch *url* via scrape.do to bypass TikTok bot detection."""
    token = os.getenv("SCRAPE_DO_TOKEN", "")
    encoded = urllib.parse.quote(url, safe="")
    scrape_url = f"http://api.scrape.do/?url={encoded}&token={token}"
    return requests.get(scrape_url, timeout=timeout)


def _extract_user_from_html(html: str, username: str) -> dict:
    """Parse authorId and secUid from TikTok profile page HTML."""
    # Pattern 1 — __UNIVERSAL_DATA_FOR_REHYDRATION__
    m = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        html, re.DOTALL,
    )
    if m:
        try:
            data = json.loads(m.group(1))
            user = (
                data.get("__DEFAULT_SCOPE__", {})
                .get("webapp.user-detail", {})
                .get("userInfo", {})
                .get("user", {})
            )
            if user.get("id"):
                return {"id": user["id"], "secUid": user.get("secUid", ""),
                        "uniqueId": user.get("uniqueId", username)}
        except (json.JSONDecodeError, KeyError):
            pass

    # Pattern 2 — SIGI_STATE
    m = re.search(r'<script id="SIGI_STATE"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            user = (
                data.get("UserPage", {})
                .get("userInfo", {})
                .get("user", {})
            )
            if user.get("id"):
                return {"id": user["id"], "secUid": user.get("secUid", ""),
                        "uniqueId": user.get("uniqueId", username)}
        except (json.JSONDecodeError, KeyError):
            pass

    return {}


class TikTokService:

    def _get_user_info(self, username: str) -> dict:
        """Fetch authorId + secUid for *username* using scrape.do."""
        resp = _scrape_do_get(f"https://www.tiktok.com/@{username}")
        resp.raise_for_status()
        return _extract_user_from_html(resp.text, username)

    def fetch_stories(self, username: str) -> dict:
        username = username.strip().lstrip("@")

        if not username:
            return {"status": "error", "message": "Username must not be empty."}

        try:
            user_info = self._get_user_info(username)
        except requests.exceptions.Timeout:
            return {"status": "error", "message": "Request timed out fetching user info."}
        except Exception as exc:
            return {"status": "error", "message": f"Could not load profile for @{username}: {exc}"}

        if not user_info.get("id"):
            return {"status": "error", "message": f"User @{username} not found on TikTok."}

        try:
            resp = requests.get(
                _STORY_API,
                headers=_HEADERS_API,
                params={
                    **_COMMON_PARAMS,
                    "authorId":  user_info["id"],
                    "secUid":    user_info["secUid"],
                    "count":     "20",
                    "cursor":    "0",
                    "from_page": "user",
                },
                timeout=10,
            )
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            return {"status": "error", "message": "Request timed out fetching stories."}
        except requests.exceptions.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else 0
            if code == 404:
                return {"status": "error", "message": f"User @{username} not found."}
            if code == 429:
                return {"status": "error", "message": "Rate limit exceeded. Please try again later."}
            return {"status": "error", "message": f"TikTok API error {code}."}
        except requests.exceptions.RequestException as exc:
            return {"status": "error", "message": f"Network error: {exc}"}

        return self._normalize(username, resp.json())

    def _normalize(self, username: str, raw: dict) -> dict:
        items = raw.get("itemList", [])
        stories = []

        for item in items:
            story_id = item.get("id", "")

            if "imagePost" in item:
                url_list = (
                    item.get("imagePost", {})
                    .get("images", [{}])[0]
                    .get("imageURL", {})
                    .get("urlList", [])
                )
                url = url_list[0] if url_list else ""
                if url:
                    stories.append({"type": "image", "url": url, "id": story_id})
            else:
                video = item.get("video", {})
                url = (
                    video.get("playAddr")
                    or (video.get("PlayAddrStruct", {}).get("UrlList") or [""])[0]
                )
                if url:
                    stories.append({"type": "video", "url": url, "id": story_id})

        if not stories and raw.get("statusCode", 0) != 0:
            return {
                "status": "error",
                "message": "TikTok returned no stories. The account may be private or have no active stories.",
            }

        return {"status": "success", "username": username, "stories": stories}
