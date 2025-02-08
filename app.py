import streamlit as st
import subprocess
import json
import pandas as pd
from datetime import datetime

st.title("WhatsApp Message Checker")

group_names = ["Tree Bowl - Internal", "BAVA- Amazon & Flipkart"]
selected_group = st.selectbox("Select Group", group_names)
selected_date = st.date_input("Select Date")

st.session_state.selected_group = selected_group
st.write(f"Selected Group: {selected_group}")

def check_messages_via_node(group_name, check_date):
    if not check_date or not group_name:
        st.error("❌ Error: Date or group is missing.")
        return None

    check_date_str = str(check_date)
    group_name_str = str(group_name)

    st.write(f"🔄 Running: node check.js \"{check_date_str}\" \"{group_name_str}\"")  # Debugging log

    process = subprocess.Popen(
        f'node check.js "{check_date_str}" "{group_name_str}"',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, shell=True, encoding="utf-8", errors="replace"
    )

    stdout, stderr = process.communicate()

    if stderr and "DeprecationWarning" not in stderr:
        st.error(f"❌ Error from Node.js: {stderr}")
        return None

    try:
        response = json.loads(stdout.strip())  # Strip whitespace to avoid JSON errors
        if 'error' in response:
            st.error(response['error'])
            return None
        return response['messageStatus']
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON response from Node.js: {stdout}")
        return None

if st.button("Check Messages"):
    check_date = selected_date.strftime("%Y-%m-%d")
    status = check_messages_via_node(selected_group, check_date)

    if status:
        # Convert dictionary to DataFrame with sender details
        df = pd.DataFrame([
            {"Time Slot": slot, "Message Status": details["status"], "Sender": details["sender"]}
            for slot, details in status.items()
        ])

        st.subheader(f"📅 Message Log for {selected_date}")
        st.table(df)

    # Show QR code if it's the first time running
    st.subheader("Scan QR Code to authenticate WhatsApp Web:")
    st.image("http://your-heroku-app-name.herokuapp.com/qr/qr.png", caption="Scan this QR Code with WhatsApp", use_column_width=True)
