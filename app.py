import requests
import pandas as pd
import streamlit as st
from PIL import Image
import io
import socketio

st.title("WhatsApp Message Checker")

group_names = [
    "Tree Bowl - Internal", "BAVA- Amazon & Flipkart", "Sarvesh Industries - Amazon", "AROLA BAMBOO - SR ECOM AMAZON", "Sowjanya Silks - Internal",
]

selected_group = st.selectbox("Select Group", group_names)
selected_date = st.date_input("Select Date")

st.sidebar.subheader("WhatsApp Connection Status")

# Socket.IO client instance
sio = socketio.Client()

# Placeholder for QR code and status messages
qr_placeholder = st.sidebar.empty()
status_placeholder = st.sidebar.empty()

def connect_to_backend():
    try:
        sio.connect("https://message-checker.onrender.com")  # Replace with your backend URL
        status_placeholder.success("Connected to WhatsApp Backend")
    except Exception as e:
        status_placeholder.error(f"Connection error: {e}")
        st.stop()

# Handle QR Code updates from the backend
@sio.on("qr")
def qr_handler(data):
    qr_code = data["qr"]  # Base64 QR code received
    qr_image = Image.open(io.BytesIO(requests.get(qr_code).content))  # Convert to an image
    qr_placeholder.image(qr_image, caption="Scan the QR code to connect to WhatsApp", use_column_width=True)

# Handle successful connection to WhatsApp
@sio.on("ready")
def ready_handler(data):
    qr_placeholder.empty()  # Remove the QR code once connected
    status_placeholder.success("WhatsApp is ready!")

# Handle disconnection
@sio.on("disconnected")
def disconnected_handler(data):
    qr_placeholder.empty()
    status_placeholder.error("Disconnected from WhatsApp. Please reconnect.")

# Connect to the backend
connect_to_backend()

# Function to check messages
def check_messages_via_api(group_name, check_date):
    if not check_date or not group_name:
        st.error("❌ Error: Date or group is missing.")
        return None

    api_url = "https://message-checker.onrender.com/check-messages"  # Replace with your backend URL
    params = {
        "date": check_date,
        "group": group_name
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise error for HTTP errors

        data = response.json()
        if 'error' in data:
            st.error(data['error'])
            return None
        return data['messageStatus']
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {e}")
        return None

if st.button("Check Messages"):
    check_date = selected_date.strftime("%Y-%m-%d")
    status = check_messages_via_api(selected_group, check_date)

    if status:
        df = pd.DataFrame([
            {"Time Slot": slot, "Message Status": details["status"], "Senders": ", ".join(details.get("senders", []))}
            for slot, details in status.items()
        ])

        st.subheader(f"📅 Message Log for {selected_date}")
        st.table(df)
