import hashlib
import uuid

import streamlit as st
from dotenv import load_dotenv

from services.instagram import InstagramService
from services.tiktok import TikTokService
from utils.media_handler import download_media_bytes
from utils.rate_limiter import RateLimiter
from utils.logger_helper import get_logger
from utils.i18n import t

load_dotenv()

logger = get_logger()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _render_footer():
    st.divider()
    st.caption(t("footer"))


@st.cache_data(ttl=300, show_spinner=False)
def _get_ig_stories(username: str) -> dict:
    return InstagramService().fetch_stories(username)


@st.cache_data(ttl=300, show_spinner=False)
def _get_tt_stories(username: str) -> dict:
    return TikTokService().fetch_stories(username)


def _get_user_key() -> str:
    try:
        headers = st.context.headers
        forwarded = headers.get("X-Forwarded-For", "").split(",")[0].strip()
        ip = forwarded or headers.get("X-Real-Ip", "").strip()
        if ip:
            return "ip_" + hashlib.sha256(ip.encode()).hexdigest()[:20]
    except Exception:
        pass
    if "guest_id" not in st.session_state:
        st.session_state["guest_id"] = f"guest_{uuid.uuid4().hex}"
    return st.session_state["guest_id"]


def _media_grid(stories: list, username: str, platform: str):
    """Render a 3-column grid of story media with download buttons."""
    cols = st.columns(3)
    for idx, story in enumerate(stories):
        col        = cols[idx % 3]
        story_id   = story.get("id", str(idx))
        story_url  = story["url"]
        story_type = story["type"]

        with col:
            if story_type == "video":
                if platform == "tiktok":
                    # TikTok CDN requires signed cookies — inline playback not possible
                    st.markdown(
                        "<div style='text-align:center;padding:32px 8px;border-radius:8px;"
                        "background:#1A1030;color:#D946EF;font-size:2rem;'>🎬</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    try:
                        st.video(story_url)
                    except Exception:
                        st.warning(t("video_unavailable"))
                with st.spinner(t("spinner_buffer")):
                    try:
                        data = download_media_bytes(story_url, platform=platform)
                        st.download_button(
                            label=t("dl_video"),
                            data=data,
                            file_name=f"{username}_story_{story_id}.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                            key=f"dl_{platform}_{idx}",
                        )
                    except Exception as exc:
                        logger.warning("Download failed %s %s story %s: %s", platform, username, story_id, exc)
                        st.warning(t("download_unavailable"))
            else:
                try:
                    st.image(story_url, use_container_width=True)
                except Exception:
                    st.warning(t("image_unavailable"))
                with st.spinner(t("spinner_buffer")):
                    try:
                        data = download_media_bytes(story_url, platform=platform)
                        st.download_button(
                            label=t("dl_image"),
                            data=data,
                            file_name=f"{username}_story_{story_id}.jpg",
                            mime="image/jpeg",
                            use_container_width=True,
                            key=f"dl_{platform}_{idx}",
                        )
                    except Exception as exc:
                        logger.warning("Download failed %s %s story %s: %s", platform, username, story_id, exc)
                        st.warning(t("download_unavailable"))


def _handle_search(platform: str, username: str, rate_limiter: RateLimiter, user_key: str):
    """Fetch stories, enforce rate limit, store result in session_state, then rerun."""
    username = username.strip().lower()

    if not username:
        st.warning(t("empty_input") if platform == "ig" else t("tt_empty_input"))
        return

    if not rate_limiter.is_allowed(user_key):
        logger.warning("Rate limit reached for user_key=%s platform=%s", user_key, platform)
        st.error(t("rate_limit_error"))
        return

    counted: set = st.session_state.setdefault("counted_queries", set())
    query_key = f"{platform}:{username}"
    is_cache_hit = query_key in counted

    with st.spinner(t("spinner_fetch")):
        if platform == "ig":
            result = _get_ig_stories(username)
        else:
            result = _get_tt_stories(username)

    if result["status"] == "error":
        logger.warning("API error platform=%s user_key=%s username=%s — %s",
                       platform, user_key, username, result["message"])
    elif not is_cache_hit:
        rate_limiter.increment_counter(user_key)
        counted.add(query_key)
        logger.info("Fetch counted platform=%s user_key=%s username=%s (remaining=%d)",
                    platform, user_key, username, rate_limiter.remaining(user_key))

    st.session_state[f"{platform}_result"]   = result
    st.session_state[f"{platform}_username"] = username
    st.rerun()


def _render_result(platform: str):
    """Display previously fetched results from session_state."""
    result   = st.session_state.get(f"{platform}_result")
    username = st.session_state.get(f"{platform}_username", "")

    if result is None:
        return

    if result["status"] == "error":
        msg = result["message"].lower()
        if any(k in msg for k in ("429", "rate limit", "quota", "too many")):
            st.warning(t("capacity_error"))
        else:
            st.error(result["message"])
        return

    stories = result.get("stories", [])
    if not stories:
        st.info(t("no_stories") if platform == "ig" else t("tt_no_stories"))
        return

    n = len(stories)
    label = t("found_stories_one") if n == 1 else t("found_stories_many", n=n)
    st.success(f"{label} **@{username}**.")
    st.divider()
    _media_grid(stories, username, platform=("instagram" if platform == "ig" else "tiktok"))


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

rate_limiter = RateLimiter()
user_key     = _get_user_key()

st.markdown(t("hero_title"))
st.markdown(t("hero_subtitle"))
st.info(t("hero_info"))

remaining = rate_limiter.remaining(user_key)
st.markdown(f"{t('quota_remaining')} **{remaining} {t('quota_of')}**")

# ---------------------------------------------------------------------------
# Platform tabs
# ---------------------------------------------------------------------------

tab_ig, tab_tt = st.tabs([t("tab_instagram"), t("tab_tiktok")])

# ── Instagram tab ──────────────────────────────────────────────────────────
with tab_ig:
    ig_username = st.text_input(
        label=t("input_label"),
        placeholder=t("input_placeholder"),
        max_chars=30,
        key="ig_username_input",
    )
    if st.button(t("search_button"), type="primary", use_container_width=True, key="ig_search"):
        _handle_search("ig", ig_username, rate_limiter, user_key)

    _render_result("ig")

# ── TikTok tab ─────────────────────────────────────────────────────────────
with tab_tt:
    tt_username = st.text_input(
        label=t("tt_input_label"),
        placeholder=t("tt_input_placeholder"),
        max_chars=30,
        key="tt_username_input",
    )
    if st.button(t("tt_search_button"), type="primary", use_container_width=True, key="tt_search"):
        _handle_search("tt", tt_username, rate_limiter, user_key)

    _render_result("tt")

_render_footer()
