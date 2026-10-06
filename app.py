import streamlit as st

from rca.ui import components as ui
from rca.ui.screens import SCREENS

st.set_page_config(page_title="RCA Analyzer", page_icon=None, layout="wide")
st.session_state.setdefault("step", 0)
st.markdown(ui.css(), unsafe_allow_html=True)
st.markdown(ui.stepper(st.session_state.step), unsafe_allow_html=True)
if st.session_state.step > 0:
    st.markdown(ui.notice_banner(), unsafe_allow_html=True)
SCREENS[st.session_state.step]()
