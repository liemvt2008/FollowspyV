import requests


def download_media_bytes(url: str) -> bytes:
    """Fetch media from *url* and return raw bytes for Streamlit download_button."""
    response = requests.get(
        url,
        stream=True,
        timeout=10,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.instagram.com/",
        },
    )
    response.raise_for_status()
    return response.content
