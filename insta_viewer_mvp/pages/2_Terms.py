import streamlit as st
from utils.i18n import t

st.markdown(t("terms_title"))
st.caption(t("terms_updated"))
st.markdown(t("terms_body"))

st.divider()
st.caption(t("footer"))
