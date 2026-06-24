import uuid

import streamlit as st
from dotenv import load_dotenv

from services.instagram import InstagramService
from utils.media_handler import download_media_bytes
from utils.rate_limiter import RateLimiter
from utils.logger_helper import get_logger
from utils.i18n import t

load_dotenv()

logger = get_logger()


# ---------------------------------------------------------------------------
# Footer helper
# ---------------------------------------------------------------------------

def _render_footer():
    st.divider()
    st.caption(t("footer"))


# ---------------------------------------------------------------------------
# Cached story fetcher
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def get_stories(username: str) -> dict:
    service = InstagramService()
    return service.fetch_stories(username)


# ---------------------------------------------------------------------------
# User identity (guest UUID, persists within session)
# ---------------------------------------------------------------------------

rate_limiter = RateLimiter()

if "guest_id" not in st.session_state:
    st.session_state["guest_id"] = f"guest_{uuid.uuid4().hex}"
user_key = st.session_state["guest_id"]

# ---------------------------------------------------------------------------
# Hero section
# ---------------------------------------------------------------------------

st.markdown(t("hero_title"))
st.markdown(t("hero_subtitle"))
st.info(t("hero_info"))

remaining = rate_limiter.remaining(user_key)
st.markdown(f"{t('quota_remaining')} **{remaining} {t('quota_of')}**")

# ---------------------------------------------------------------------------
# Search form
# ---------------------------------------------------------------------------

username_input = st.text_input(
    label=t("input_label"),
    placeholder=t("input_placeholder"),
    max_chars=30,
    key="username_input",
)

search_clicked = st.button(t("search_button"), type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Search logic
# ---------------------------------------------------------------------------

if search_clicked:
    username = username_input.strip().lower()

    if not username:
        st.warning(t("empty_input"))

    elif not rate_limiter.is_allowed(user_key):
        logger.warning("Rate limit reached for user_key=%s", user_key)
        st.error(t("rate_limit_error"))

    else:
        counted_usernames: set = st.session_state.setdefault("counted_usernames", set())
        is_cache_hit = username in counted_usernames

        with st.spinner(t("spinner_fetch")):
            result = get_stories(username)

        if result["status"] == "error":
            logger.warning(
                "API error for user_key=%s username=%s — %s",
                user_key, username, result["message"],
            )
        elif not is_cache_hit:
            rate_limiter.increment_counter(user_key)
            counted_usernames.add(username)
            logger.info(
                "Fetch counted for user_key=%s username=%s (remaining=%d)",
                user_key, username, rate_limiter.remaining(user_key),
            )

        st.session_state["result"] = result
        st.session_state["searched_username"] = username
        st.rerun()

# ---------------------------------------------------------------------------
# Render results
# ---------------------------------------------------------------------------

result   = st.session_state.get("result")
username = st.session_state.get("searched_username", "")

if result is None:
    _render_footer()
    st.stop()

if result["status"] == "error":
    msg = result["message"].lower()
    if any(k in msg for k in ("429", "rate limit", "quota", "too many")):
        st.warning(t("capacity_error"))
    else:
        st.error(result["message"])
    _render_footer()
    st.stop()

stories = result.get("stories", [])

if not stories:
    st.info(t("no_stories"))
    _render_footer()
    st.stop()

n = len(stories)
label = t("found_stories_one") if n == 1 else t("found_stories_many", n=n)
st.success(f"{label} **@{username}**.")

st.divider()

# ---------------------------------------------------------------------------
# 3-column media grid with download buttons
# ---------------------------------------------------------------------------

cols = st.columns(3)

for idx, story in enumerate(stories):
    col        = cols[idx % 3]
    story_id   = story.get("id", str(idx))
    story_url  = story["url"]
    story_type = story["type"]

    with col:
        if story_type == "video":
            try:
                st.video(story_url)
            except Exception:
                st.warning(t("video_unavailable"))
            with st.spinner(t("spinner_buffer")):
                try:
                    media_bytes = download_media_bytes(story_url)
                    st.download_button(
                        label=t("dl_video"),
                        data=media_bytes,
                        file_name=f"{username}_story_{story_id}.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                        key=f"dl_{idx}",
                    )
                except Exception as exc:
                    logger.warning("Download failed %s story %s: %s", username, story_id, exc)
                    st.warning(t("download_unavailable"))
        else:
            try:
                st.image(story_url, use_container_width=True)
            except Exception:
                st.warning(t("image_unavailable"))
            with st.spinner(t("spinner_buffer")):
                try:
                    media_bytes = download_media_bytes(story_url)
                    st.download_button(
                        label=t("dl_image"),
                        data=media_bytes,
                        file_name=f"{username}_story_{story_id}.jpg",
                        mime="image/jpeg",
                        use_container_width=True,
                        key=f"dl_{idx}",
                    )
                except Exception as exc:
                    logger.warning("Download failed %s story %s: %s", username, story_id, exc)
                    st.warning(t("download_unavailable"))

_render_footer()
