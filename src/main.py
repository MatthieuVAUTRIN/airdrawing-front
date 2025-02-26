import cv2
import streamlit as st

from services.api import change_color, clear_canvas
from services.websocket import WebSocketClient


def try_open_camera():
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        return cap
    return None


# WebSocket client and camera in session state if not already there for persistance
if "client" not in st.session_state:
    st.session_state.client = WebSocketClient()

if "camera" not in st.session_state:
    st.session_state.camera = None

st.title("Webcam Live Airdrawing")
st.empty()
st.markdown(
    """
    ---

    This app allows you to draw on the screen using your index finger.

    You can also erase the drawing by using your index and middle finger together.

    You can change the color of the drawing or erase it using the sidebar buttons.

    ---
    """
)
enabled = st.checkbox("Camera On", value=False)

if enabled:
    if st.session_state.camera is None:
        st.session_state.camera = try_open_camera()
        if st.session_state.camera is None:
            st.error("No camera found. Please check your camera connection.")
            st.stop()
        else:
            st.session_state.camera.set(cv2.CAP_PROP_FPS, 30)
            st.session_state.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            st.session_state.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    camera = st.session_state.camera

    frames = st.image([], use_container_width=True)

    # start WebSocket client if not already running
    if not hasattr(st.session_state.client, "thread"):
        st.session_state.client.start()

    # main loop for reading frmaes + display
    while enabled:
        ret, frame = camera.read()
        if not ret:
            st.error("Failed to grab frame from camera")
            break

        # here we flip frame for better user experience
        frame = cv2.flip(frame, 1)
        st.session_state.client.frame_queue.put(frame)

        # check if there is any processed frame from the WebSocket client
        if not st.session_state.client.result_queue.empty():
            processed_frame = st.session_state.client.result_queue.get()
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)
            frames.image(processed_frame)

COLORS = {
    "Blue": {"rgb": (255, 0, 0), "emoji": "🟦"},
    "Green": {"rgb": (0, 255, 0), "emoji": "🟩"},
    "Red": {"rgb": (0, 0, 255), "emoji": "🟥"},
    "Yellow": {"rgb": (0, 255, 255), "emoji": "🟨"},
    "Orange": {"rgb": (0, 165, 255), "emoji": "🟧"},
    "Purple": {"rgb": (128, 0, 128), "emoji": "🟪"},
}


with st.sidebar:
    st.button(
        "Clear Drawing", on_click=clear_canvas, use_container_width=True, icon="🗑️"
    )

    st.markdown("---")
    st.markdown("#### Choose Color")
    st.write("\n")

    for color_name, color_info in COLORS.items():
        st.button(
            f"{color_name}",
            on_click=change_color,
            args=(color_info["rgb"],),
            icon=color_info["emoji"],
            use_container_width=True,
        )
