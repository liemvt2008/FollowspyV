import requests

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

_REFERERS = {
    "instagram": "https://www.instagram.com/",
    "tiktok":    "https://www.tiktok.com/",
}


def download_media_bytes(url: str, platform: str = "instagram") -> bytes:
    """Fetch media from *url* and return raw bytes for Streamlit download_button."""
    response = requests.get(
        url,
        stream=True,
        timeout=15,
        headers={
            "User-Agent": _UA,
            "Referer":    _REFERERS.get(platform, _REFERERS["instagram"]),
            "Accept":     "*/*",
        },
    )
    response.raise_for_status()
    return response.content
