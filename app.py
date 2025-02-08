import streamlit as st
import requests

# Title for the Streamlit app
st.title("WhatsApp Message Checker")

# Select Group and Date
group_names = ["Tree Bowl - Internal", "BAVA- Amazon & Flipkart"]
selected_group = st.selectbox("Select Group", group_names)
selected_date = st.date_input("Select Date")

st.session_state.selected_group = selected_group
st.write(f"Selected Group: {selected_group}")

# Function to fetch QR code image from the Node.js server
def fetch_qr_code():
    try:
        url = "http://localhost:3000/qr"  # This should be your Node.js URL, change localhost to the deployed URL
        response = requests.get(url)
        if response.status_code == 200:
            # Extract QR code image URL from the HTML response
            start_index = response.text.find('src="') + 5
            end_index = response.text.find('"', start_index)
            qr_code_url = response.text[start_index:end_index]
            return qr_code_url
        else:
            st.error("❌ Error fetching QR code.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Display QR code from the Node.js server
qr_code_url = fetch_qr_code()
if qr_code_url:
    st.subheader("Scan this QR code with WhatsApp Web to authenticate")
    st.image(qr_code_url)  # This will display the QR code

# If user clicks on 'Check Messages', check the messages for the selected date and group
if st.button("Check Messages"):
    # Add functionality to fetch message status for the selected group and date here
    st.write(f"Checking messages for {selected_group} on {selected_date}")
