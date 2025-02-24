import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"


def clear_canvas():
    try:
        response = requests.post(f"{BACKEND_URL}/clear-canvas", timeout=5)
        if response.status_code != 200:
            st.error("Failed to clear canvas")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")


def change_color(color):
    try:
        response = requests.post(
            f"{BACKEND_URL}/change-color", json={"color": color}, timeout=5
        )
        if response.status_code != 200:
            st.error("Failed to change color")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
