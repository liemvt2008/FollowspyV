import streamlit as st
from utils.i18n import t

st.markdown(t("privacy_title"))
st.caption(t("privacy_updated"))
st.markdown(t("privacy_body"))

st.divider()
st.caption(t("footer"))
