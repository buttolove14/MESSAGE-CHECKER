import streamlit as st
import re
import pandas as pd
from datetime import datetime, time

# Function to parse WhatsApp chat
def parse_chat(file):
    messages = []
    pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - (.*?): (.*)"

    for line in file:
        match = re.match(pattern, line)
        if match:
            date = match.group(1)
            msg_time = match.group(2)
            sender = match.group(3)
            message = match.group(4)
            timestamp = f"{date} {msg_time}"
            messages.append([timestamp, date, msg_time, sender, message])

    df = pd.DataFrame(messages, columns=["Timestamp", "Date", "Time", "Sender", "Message"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%d/%m/%y %H:%M", errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%y", errors="coerce")
    return df

# Function to filter messages in a given time range
def check_messages_in_range(df, check_date, start_time, end_time):
    start_datetime = datetime.combine(check_date, start_time)
    end_datetime = datetime.combine(check_date, end_time)
    return df[(df["Timestamp"] >= start_datetime) & (df["Timestamp"] <= end_datetime)]

# Streamlit UI
st.title("Message Time Checker")

uploaded_file = st.file_uploader("Upload WhatsApp Chat (.txt)", type="txt")

if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8").split("\n")
    df = parse_chat(file_content)

    # User selects date
    check_date = st.date_input("Select Date to Check Messages")

    # Filter chat to show only selected date's messages
    filtered_df = df[df["Date"] == pd.to_datetime(check_date)]

    # Show only selected date's messages
    st.write(f"Messages on {check_date}:")
    if not filtered_df.empty:
        st.dataframe(filtered_df)
    else:
        st.warning(f"❌ No messages found on {check_date}")

    # Predefined time ranges
    time_ranges = [
        ("10:00 AM - 10:30 AM", time(10, 0), time(10, 30)),
        ("12:00 PM - 12:30 PM", time(12, 0), time(12, 30)),
        ("3:30 PM - 4:00 PM", time(15, 30), time(16, 0))
    ]

    # Checking messages in each time range
    for label, start_time, end_time in time_ranges:
        messages_found = check_messages_in_range(filtered_df, check_date, start_time, end_time)

        st.subheader(f"⏰ Checking: {label}")
        if not messages_found.empty:
            st.success(f"✅ Messages were sent in this time range!")
            st.write(messages_found)
        else:
            st.warning(f"❌ No messages found in this time range.")
