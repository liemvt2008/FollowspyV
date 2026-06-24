import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from dotenv import load_dotenv

from utils.i18n import t

load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="IG Story Viewer — Anonymous & Free",
    page_icon="🕵️",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Language switcher — top right
# ---------------------------------------------------------------------------

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

_, lang_col = st.columns([6, 1])
with lang_col:
    if st.button(t("lang_toggle"), use_container_width=True):
        st.session_state["lang"] = "vi" if st.session_state["lang"] == "en" else "en"
        st.rerun()

# ---------------------------------------------------------------------------
# Analytics — Google Analytics (optional)
# ---------------------------------------------------------------------------

_GA_ID = os.getenv("GA_MEASUREMENT_ID", "")
if _GA_ID:
    st.markdown(
        f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={_GA_ID}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());
            gtag('config', '{_GA_ID}', {{anonymize_ip: true}});
        </script>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Shared auth setup (state persists across all pages via session_state)
# ---------------------------------------------------------------------------

_CONFIG_PATH = Path(__file__).parent / "config_auth.yaml"
try:
    with open(_CONFIG_PATH) as f:
        auth_config = yaml.load(f, Loader=SafeLoader)
except FileNotFoundError:
    auth_config = yaml.safe_load(st.secrets["CONFIG_AUTH_YAML"])

_cookie_secret = os.getenv("COOKIE_SECRET")
if not _cookie_secret:
    try:
        _cookie_secret = st.secrets.get("COOKIE_SECRET")
    except Exception:
        pass
cookie_key = _cookie_secret or auth_config["cookie"]["key"]

authenticator = stauth.Authenticate(
    auth_config["credentials"],
    auth_config["cookie"]["name"],
    cookie_key,
    auth_config["cookie"]["expiry_days"],
)

st.session_state["_authenticator"] = authenticator
st.session_state["_auth_config"] = auth_config

with st.sidebar:
    st.markdown(t("sidebar_login"))
    authenticator.login(location="sidebar")
    if st.session_state.get("authentication_status"):
        authenticator.logout(location="sidebar")

# ---------------------------------------------------------------------------
# Multi-page navigation
# ---------------------------------------------------------------------------

pg = st.navigation(
    [
        st.Page("pages/1_Viewer.py",  title="Story Viewer",    icon="🕵️", default=True),
        st.Page("pages/2_Terms.py",   title="Terms of Service", icon="📜"),
        st.Page("pages/3_Privacy.py", title="Privacy Policy",  icon="🔒"),
    ]
)
pg.run()

# ---------------------------------------------------------------------------
# Umami Analytics — invisible, fires on every page
# ---------------------------------------------------------------------------

_UMAMI_SCRIPT = """
<script defer src="https://cloud.umami.is/script.js"
        data-website-id="5050b923-63be-43bc-b746-9d87a87bedf5"></script>
"""
components.html(_UMAMI_SCRIPT, height=0, width=0)
