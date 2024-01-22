from main import (
        page_config,
        load_url,
        body
        )
import streamlit as st


if __name__ == "__main__":
    page_config()

    load_url(local_cache=False)
    if "url" in st.session_state:
        body()
