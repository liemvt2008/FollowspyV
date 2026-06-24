import os
import re
import json

import requests
from dotenv import load_dotenv

load_dotenv()

_USERNAME_RE = re.compile(r"^[a-z0-9._]+$")


class InstagramService:
    """Wraps the RapidAPI Instagram Scraper endpoint for story fetching."""

    _API_URL = "https://instagram-scraper-api2.p.rapidapi.com/v1/stories"

    def __init__(self):
        self._key = os.getenv("RAPIDAPI_KEY")
        self._host = os.getenv("RAPIDAPI_HOST")
        if not self._key or not self._host:
            raise ValueError(
                "RAPIDAPI_KEY and RAPIDAPI_HOST must be set in the environment."
            )
        self._headers = {
            "x-rapidapi-key": self._key,
            "x-rapidapi-host": self._host,
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_stories(self, username: str) -> dict:
        """Fetch and normalise stories for *username*.

        Returns a dict with keys ``status``, and on success ``username``
        and ``stories``.  On failure the key ``message`` describes the error.
        """
        username = username.strip().lower()

        if not username:
            return {"status": "error", "message": "Username must not be empty."}

        if not _USERNAME_RE.match(username):
            return {
                "status": "error",
                "message": (
                    "Invalid username. Only letters, digits, '.' and '_' are allowed."
                ),
            }

        try:
            response = requests.get(
                self._API_URL,
                headers=self._headers,
                params={"username_or_id_or_url": username},
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Request timed out. Please try again.",
            }
        except requests.exceptions.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else 0
            if status_code == 404:
                return {"status": "error", "message": f"User '{username}' not found."}
            if status_code == 401:
                return {
                    "status": "error",
                    "message": "Unauthorised — check your RapidAPI key.",
                }
            if status_code == 429:
                return {
                    "status": "error",
                    "message": "Rate limit exceeded. Please wait and try again.",
                }
            return {
                "status": "error",
                "message": f"API error {status_code}: {exc}",
            }
        except requests.exceptions.RequestException as exc:
            return {"status": "error", "message": f"Network error: {exc}"}

        raw = response.json()
        return self._normalise(username, raw)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalise(self, username: str, raw: dict) -> dict:
        """Convert the raw vendor response into the internal unified format."""
        stories = []

        # The API wraps items in data.reels_media[].items or data.items
        data = raw.get("data", raw)
        items = (
            data.get("items")
            or _flatten_reels_media(data.get("reels_media", []))
            or []
        )

        for item in items:
            media_type = "video" if item.get("is_video") else "image"
            url = _best_url(item)
            if url:
                stories.append(
                    {
                        "type": media_type,
                        "url": url,
                        "id": str(item.get("pk") or item.get("id") or ""),
                    }
                )

        return {"status": "success", "username": username, "stories": stories}


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------

def _flatten_reels_media(reels_media: list) -> list:
    items = []
    for reel in reels_media:
        items.extend(reel.get("items", []))
    return items


def _best_url(item: dict) -> str:
    """Return the highest-resolution URL for an item."""
    # Video: prefer video_versions list
    if item.get("is_video"):
        versions = item.get("video_versions") or []
        if versions:
            return versions[0].get("url", "")

    # Image: actual API response uses image_versions.items (sorted best-first)
    candidates = (item.get("image_versions") or {}).get("items") or []
    if candidates:
        return candidates[0].get("url", "")

    # Fallback: some items expose a flat thumbnail_url
    return item.get("thumbnail_url") or item.get("url", "")


# ------------------------------------------------------------------
# Sanity test  (python services/instagram.py)
# ------------------------------------------------------------------

if __name__ == "__main__":
    service = InstagramService()
    result = service.fetch_stories("leomessi")
    print(json.dumps(result, indent=2))
