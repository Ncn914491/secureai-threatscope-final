import streamlit as st
import os
from vertexai.preview.generative_models import GenerativeModel
import vertexai
from auth import login
from analyzer import initialize_history, log_analysis, show_history

# --- Session & Login ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
    st.stop()

# --- GCP Vertex AI Initialization ---
PROJECT_ID = "freetrailproject-463104"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.5-flash")

# --- Streamlit Page Config ---
st.set_page_config(page_title="SecureAI ThreatScope", layout="wide")
st.title("🛡️ SecureAI ThreatScope")
st.subheader("AI-Driven Threat Analyzer using Gemini 2.5 Flash")
st.markdown("---")

# --- Initialize Log History ---
initialize_history()

# --- Threat Input ---
st.header("📝 Input Log or Alert")
log_input = st.text_area(
    "Paste your log, IDS alert, or firewall event:",
    height=300,
    placeholder="[ALERT] Failed SSH login from IP 192.168.1.101 on port 22..."
)

# --- Threat Analysis Trigger ---
if st.button("Analyze Threat 🚨") and log_input.strip():
    with st.spinner("Analyzing with Gemini 2.5 Flash..."):
        try:
            prompt = f"""
You are a cybersecurity analyst AI.

Given this log data, provide:
1. Threat summary
2. Severity level
3. Suggested remediation steps
4. Suspicious IPs, domains, or ports

Log:
{log_input.strip()}
"""
            response = model.generate_content(prompt)
            result = response.text

            st.subheader("✅ Threat Summary Generated:")
            st.markdown(result)
            log_analysis(log_input.strip(), result)

        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")

# --- History Viewer ---
st.markdown("---")
show_history()
st.caption("Powered by Google Vertex AI + Streamlit | SecureAI ThreatScope – 2025")
