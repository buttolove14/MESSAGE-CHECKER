import requests
import pandas as pd
import streamlit as st
from streamlit_qrcode import qrcode
import socketio

st.title("WhatsApp Message Checker")

group_names = [
    "Tree Bowl - Internal", "BAVA- Amazon & Flipkart", "Sarvesh Industries - Amazon", "AROLA BAMBOO - SR ECOM AMAZON", "Sowjanya Silks - Internal",
    # Add the rest of the group names here
]

selected_group = st.selectbox("Select Group", group_names)
selected_date = st.date_input("Select Date")

st.sidebar.subheader("WhatsApp Connection Status")

# Socket.IO connection
sio = socketio.Client()

@st.cache_data(ttl=60)
def connect_to_whatsapp():
    try:
        sio.connect("http://your-node-backend-url")  # Replace with your backend URL
        st.sidebar.success("Connected to WhatsApp Backend")
    except Exception as e:
        st.sidebar.error("Could not connect to backend.")
        st.stop()

def display_qr_code():
    qr_placeholder = st.sidebar.empty()
    status_placeholder = st.sidebar.empty()

    @sio.on("qr")
    def qr_handler(data):
        qr_code = data["qr"]
        qr_placeholder.image(qr_code, caption="Scan this QR code to connect to WhatsApp")
        status_placeholder.info("Waiting for WhatsApp login...")

    @sio.on("ready")
    def ready_handler(data):
        qr_placeholder.empty()
        status_placeholder.success("WhatsApp is ready!")

    connect_to_whatsapp()

display_qr_code()

def check_messages_via_api(group_name, check_date):
    if not check_date or not group_name:
        st.error("❌ Error: Date or group is missing.")
        return None

    api_url = "https://your-node-backend-url/check-messages"  # Replace with your backend URL
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
