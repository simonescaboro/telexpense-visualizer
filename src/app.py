import streamlit as st

from visualizer import body, load_url, page_config

if __name__ == "__main__":
    page_config()

    load_url(local_cache=False)
    if "url" in st.session_state:
        body()
