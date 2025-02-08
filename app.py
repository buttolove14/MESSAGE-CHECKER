import streamlit as st
import requests

st.title("WhatsApp Message Checker")

# Define groups and date selection
group_names = ["Tree Bowl - Internal", "BAVA- Amazon & Flipkart"]
selected_group = st.selectbox("Select Group", group_names)
selected_date = st.date_input("Select Date")

st.session_state.selected_group = selected_group
st.write(f"Selected Group: {selected_group}")

# Function to fetch QR code from Node.js API
def fetch_qr_code():
    url = "https://your-node-server-url/qr"  # Replace with your Render Node.js URL
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # If your QR code is text-based (adjust accordingly if image)
        else:
            st.error("❌ Error fetching QR code from Node.js server.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Display the QR code
qr_code = fetch_qr_code()
if qr_code:
    st.subheader("Scan this QR code with WhatsApp Web to authenticate")
    st.code(qr_code)  # For text-based QR (adjust if you want image-based QR code)
