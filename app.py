import streamlit as st
import requests

st.title("WhatsApp Message Checker")

# Select Group and Date
group_names = ["Tree Bowl - Internal", "BAVA- Amazon & Flipkart"]
selected_group = st.selectbox("Select Group", group_names)
selected_date = st.date_input("Select Date")

st.session_state.selected_group = selected_group
st.write(f"Selected Group: {selected_group}")

# Fetch QR code from the Node.js server
def fetch_qr_code():
    url = "https://message-checker.onrender.com/qr"  # Your Render URL for Node.js
    try:
        response = requests.get(url)
        if response.status_code == 200:
            start_index = response.text.find('src="') + 5
            end_index = response.text.find('"', start_index)
            qr_code_url = response.text[start_index:end_index]
            return qr_code_url
        else:
            st.error("❌ Error fetching QR code from Node.js server.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Display the QR code image
qr_code_url = fetch_qr_code()
if qr_code_url:
    st.subheader("Scan this QR code with WhatsApp Web to authenticate")
    st.image(qr_code_url)  # Display QR code image

# Check messages after scanning QR
if st.button("Check Messages"):
    check_date = selected_date.strftime("%Y-%m-%d")
    response = requests.get(f"https://message-checker.onrender.com/check-messages?date={check_date}&group={selected_group}")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            message_status = data["messageStatus"]
            st.subheader(f"📅 Message Log for {selected_date}")
            for slot, details in message_status.items():
                st.write(f"{slot}: {details['status']} by {details['sender']}")
        else:
            st.error("❌ Error: Could not fetch message status.")
