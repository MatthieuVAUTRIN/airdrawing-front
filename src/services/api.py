import streamlit as st

BACKEND_URL = "http://localhost:8000"


def clear_canvas():
    import requests

    try:
        response = requests.post(f"{BACKEND_URL}/clear-canvas", timeout=5)
        if response.status_code != 200:
            st.error("Failed to clear canvas")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
