import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import re

# Gemini & Vertex AI
from vertexai.language_models import ChatModel
import vertexai

# --- Config ---
LOG_FILE = "logs.csv"
ABUSEIPDB_KEY = "b958d3ac03dc074ffe34998e67414ac7dbf39327be9777d2feeabb45f3888212474ec24e38fc8505"

# --- Init Vertex AI ---
vertexai.init(project="freetrailproject-463104", location="us-central1")

# --- Init Log File ---
def initialize_history():
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=["Timestamp", "Query"]).to_csv(LOG_FILE, index=False)

# --- IP Format Check ---
def is_ip(text):
    return re.match(r"^\d{1,3}(\.\d{1,3}){3}$", text)

# --- AbuseIPDB Threat Check ---
def check_ip_threat(ip):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": ABUSEIPDB_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()["data"]
        st.markdown("### 🌐 IP Threat Intelligence")
        st.write(f"**Reputation Score:** {data['abuseConfidenceScore']} / 100")
        st.write(f"**Last Reported:** {data['lastReportedAt']}")
        st.write(f"**Total Reports:** {data['totalReports']}")
    except Exception as e:
        st.warning(f"AbuseIPDB lookup failed: {e}")

# --- Gemini Threat Summary ---
def gemini_enrich(text):
    try:
        chat_model = ChatModel.from_pretrained("chat-bison")
        chat = chat_model.start_chat()
        prompt = f"""
        You are a cybersecurity analyst assistant. Analyze the following log or threat indicator. 
        Provide a summary and recommended remediation steps: 
        "{text}"
        """
        response = chat.send_message(prompt)
        st.markdown("### 🧠 Gemini Threat Summary")
        st.markdown(response.text)
    except Exception as e:
        st.warning(f"Gemini API failed: {e}")

# --- Main Analysis Logging + Enrichment ---
def log_analysis(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"✅ Analysis complete for: {text}")
    st.info(f"🕒 Logged at: {timestamp}")

    pd.DataFrame([[timestamp, text]], columns=["Timestamp", "Query"]).to_csv(
        LOG_FILE, mode='a', header=False, index=False
    )

    if is_ip(text):
        check_ip_threat(text)
    else:
        st.write("ℹ️ No IP format detected — skipping AbuseIPDB check.")

    gemini_enrich(text)

# --- History Display ---
def show_history():
    st.subheader("📊 Query History")
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)

        search_term = st.text_input("🔎 Search logs")
        if search_term:
            df = df[df["Query"].str.contains(search_term, case=False)]

        st.dataframe(df[::-1])  # Show latest first
        st.download_button("📥 Download CSV", df.to_csv(index=False), "secureai_logs.csv")
    else:
        st.info("No log data found.")
