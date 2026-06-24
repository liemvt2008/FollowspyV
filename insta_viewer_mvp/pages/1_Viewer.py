import uuid

import streamlit as st
from dotenv import load_dotenv

from services.instagram import InstagramService
from utils.media_handler import download_media_bytes
from utils.rate_limiter import RateLimiter
from utils.logger_helper import get_logger

load_dotenv()

logger = get_logger()

# ---------------------------------------------------------------------------
# Cached story fetcher
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def get_stories(username: str) -> dict:
    service = InstagramService()
    return service.fetch_stories(username)


# ---------------------------------------------------------------------------
# User identity & VIP check (auth state set by app.py router)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Footer helper — defined early so early-exit paths can call it
# ---------------------------------------------------------------------------

def _render_footer():
    st.divider()
    st.caption(
        "This application is an independent public media proxy tool. "
        "Please read our [Terms of Service](2_Terms) and [Privacy Policy](3_Privacy)."
    )


rate_limiter = RateLimiter()

_auth_status = st.session_state.get("authentication_status")
_username = st.session_state.get("username")
_auth_config = st.session_state.get("_auth_config", {})

if _auth_status and _username:
    user_key = _username
    is_vip = (
        _auth_config.get("credentials", {})
        .get("usernames", {})
        .get(_username, {})
        .get("role") == "vip"
    )
    logger.info("Authenticated session for VIP user: %s", _username)
else:
    if "guest_id" not in st.session_state:
        st.session_state["guest_id"] = f"guest_{uuid.uuid4().hex}"
    user_key = st.session_state["guest_id"]
    is_vip = False

# ---------------------------------------------------------------------------
# Hero section
# ---------------------------------------------------------------------------

st.markdown("# 🕵️ IG Story Viewer")
st.markdown("**View Instagram stories anonymously — no login, no trace.**")
st.info("Enter a public Instagram username below and click **View Stories Now**.")

if is_vip:
    st.success(f"⭐ VIP access — unlimited searches, logged in as **{_username}**.")
else:
    remaining = rate_limiter.remaining(user_key)
    st.markdown(f"⭐ Free searches remaining today: **{remaining} / 5**")

# ---------------------------------------------------------------------------
# Search form
# ---------------------------------------------------------------------------

username_input = st.text_input(
    label="Instagram Username",
    placeholder="e.g. cristiano_ronaldo",
    max_chars=30,
    key="username_input",
)

search_clicked = st.button("View Stories Now", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Search logic
# ---------------------------------------------------------------------------

if search_clicked:
    username = username_input.strip().lower()

    if not username:
        st.warning("Please enter an Instagram username.")

    elif not is_vip and not rate_limiter.is_allowed(user_key):
        logger.warning("Rate limit reached for user_key=%s", user_key)
        st.error(
            "🚫 Daily Limit Reached! You have exhausted your 5 free daily anonymous "
            "views. Please return tomorrow or sign in as a VIP user."
        )

    else:
        counted_usernames: set = st.session_state.setdefault("counted_usernames", set())
        is_cache_hit = username in counted_usernames

        with st.spinner("Fetching secure media stream..."):
            result = get_stories(username)

        if result["status"] == "error":
            logger.warning(
                "API error for user_key=%s username=%s — %s",
                user_key, username, result["message"],
            )
        elif not is_cache_hit and not is_vip:
            rate_limiter.increment_counter(user_key)
            counted_usernames.add(username)
            logger.info(
                "Fetch counted for user_key=%s username=%s (remaining=%d)",
                user_key, username, rate_limiter.remaining(user_key),
            )

        st.session_state["result"] = result
        st.session_state["searched_username"] = username

        if not is_vip:
            st.rerun()

# ---------------------------------------------------------------------------
# Render results
# ---------------------------------------------------------------------------

result = st.session_state.get("result")
username = st.session_state.get("searched_username", "")

if result is None:
    _render_footer()
    st.stop()

if result["status"] == "error":
    msg = result["message"].lower()
    if any(k in msg for k in ("429", "rate limit", "quota", "too many")):
        st.warning(
            "⚠️ Server Capacity Peak Reached. Our team is adjusting throughput, "
            "please try again shortly."
        )
    else:
        st.error(result["message"])
    _render_footer()
    st.stop()

stories = result.get("stories", [])

if not stories:
    st.info("This user currently has no stories published in the last 24 hours.")
    _render_footer()
    st.stop()

st.success(
    f"Found **{len(stories)}** stor{'y' if len(stories) == 1 else 'ies'} "
    f"for **@{username}**."
)

st.divider()

# ---------------------------------------------------------------------------
# 3-column media grid with download buttons
# ---------------------------------------------------------------------------

cols = st.columns(3)

for idx, story in enumerate(stories):
    col = cols[idx % 3]
    story_id = story.get("id", str(idx))
    story_url = story["url"]
    story_type = story["type"]

    with col:
        if story_type == "video":
            try:
                st.video(story_url)
            except Exception:
                st.warning("Video unavailable.")
            with st.spinner("Buffering…"):
                try:
                    media_bytes = download_media_bytes(story_url)
                    st.download_button(
                        label="📥 Download Video",
                        data=media_bytes,
                        file_name=f"{username}_story_{story_id}.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                        key=f"dl_{idx}",
                    )
                except Exception as exc:
                    logger.warning("Download failed %s story %s: %s", username, story_id, exc)
                    st.warning("Download unavailable.")
        else:
            try:
                st.image(story_url, use_container_width=True)
            except Exception:
                st.warning("Image unavailable.")
            with st.spinner("Buffering…"):
                try:
                    media_bytes = download_media_bytes(story_url)
                    st.download_button(
                        label="📥 Download Image",
                        data=media_bytes,
                        file_name=f"{username}_story_{story_id}.jpg",
                        mime="image/jpeg",
                        use_container_width=True,
                        key=f"dl_{idx}",
                    )
                except Exception as exc:
                    logger.warning("Download failed %s story %s: %s", username, story_id, exc)
                    st.warning("Download unavailable.")

_render_footer()
