import requests
import pandas as pd
import streamlit as st
import socketio
from PIL import Image
from io import BytesIO
import base64

st.title("WhatsApp Message Checker")

# Define group names
group_names = [
    "Tree Bowl - Internal", "BAVA- Amazon & Flipkart", "Sarvesh Industries - Amazon", "AROLA BAMBOO - SR ECOM AMAZON", "Sowjanya Silks - Internal",
]

selected_group = st.selectbox("Select Group", group_names)
selected_date = st.date_input("Select Date")

# Sidebar for connection status
st.sidebar.subheader("WhatsApp Connection Status")

# Socket.IO connection setup using socketio package
sio = socketio.Client()

# Placeholders for QR code and status messages
qr_placeholder = st.sidebar.empty()
status_placeholder = st.sidebar.empty()

# Socket.IO event for handling QR code
@sio.event
def connect():
    st.sidebar.success("Connected to WebSocket!")

@sio.event
def connect_error(data):
    st.sidebar.error(f"❌ WebSocket connection failed: {data}")

@sio.event
def disconnect():
    st.sidebar.error("❌ Disconnected from WebSocket.")

@sio.event
def qr(data):
    try:
        qr_data = data["qr"]
        decoded_qr = base64.b64decode(qr_data.split(",")[1])  # Decode the base64 QR data
        qr_image = Image.open(BytesIO(decoded_qr))
        qr_placeholder.image(qr_image, caption="Scan this QR code to connect to WhatsApp")
        status_placeholder.info("Waiting for WhatsApp login...")
    except Exception as e:
        st.sidebar.error(f"❌ Error displaying QR: {e}")

@sio.event
def ready(data):
    qr_placeholder.empty()
    status_placeholder.success("WhatsApp is ready!")

@sio.event
def disconnected(data):
    status_placeholder.error("WhatsApp disconnected. Please refresh and reconnect.")

# Connect to WebSocket
try:
    sio.connect("https://message-checker.onrender.com")  # Replace with your backend's Socket.IO URL
except Exception as e:
    st.sidebar.error(f"❌ Failed to connect to WebSocket: {e}")

# API function to check messages
def check_messages_via_api(group_name, check_date):
    if not check_date or not group_name:
        st.error("❌ Error: Date or group is missing.")
        return None

    api_url = "https://message-checker.onrender.com/check-messages"
    params = {"date": check_date, "group": group_name}

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()

        data = response.json()
        if "error" in data:
            st.error(data["error"])
            return None
        return data["messageStatus"]
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {e}")
        return None

# Button to check messages
if st.button("Check Messages"):
    check_date = selected_date.strftime("%Y-%m-%d")
    status = check_messages_via_api(selected_group, check_date)

    if status:
        df = pd.DataFrame([{
            "Time Slot": slot, 
            "Message Status": details["status"], 
            "Senders": ", ".join(details.get("senders", []))
        } for slot, details in status.items()])
        st.subheader(f"📅 Message Log for {selected_date}")
        st.table(df)
