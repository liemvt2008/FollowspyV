import os
from pathlib import Path

import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from dotenv import load_dotenv

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
# Analytics injection (zero layout shift)
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
    # On Streamlit Cloud: store the full YAML content in Secrets as CONFIG_AUTH_YAML
    auth_config = yaml.safe_load(st.secrets["CONFIG_AUTH_YAML"])

cookie_key = os.getenv("COOKIE_SECRET") or st.secrets.get("COOKIE_SECRET") or auth_config["cookie"]["key"]

authenticator = stauth.Authenticate(
    auth_config["credentials"],
    auth_config["cookie"]["name"],
    cookie_key,
    auth_config["cookie"]["expiry_days"],
)

# Store authenticator in session so pages can access logout
st.session_state["_authenticator"] = authenticator
st.session_state["_auth_config"] = auth_config

with st.sidebar:
    st.markdown("### 🔑 VIP Login")
    authenticator.login(location="sidebar")
    if st.session_state.get("authentication_status"):
        authenticator.logout(location="sidebar")

# ---------------------------------------------------------------------------
# Multi-page navigation
# ---------------------------------------------------------------------------

pg = st.navigation(
    [
        st.Page("pages/1_Viewer.py",  title="Story Viewer",   icon="🕵️", default=True),
        st.Page("pages/2_Terms.py",   title="Terms of Service", icon="📜"),
        st.Page("pages/3_Privacy.py", title="Privacy Policy",  icon="🔒"),
    ]
)
pg.run()
