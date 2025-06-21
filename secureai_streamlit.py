import streamlit as st
import datetime
from login import login
from history import display_history
from rules import custom_rules_analysis
from gemini import gemini_threat_analysis

# Set page config
st.set_page_config(page_title="SecureAI ThreatScope", layout="wide")
st.markdown("## 🛡️ SecureAI ThreatScope")

# Authenticate user
auth_status, authenticator, name = login()

if auth_status:
    st.sidebar.success(f"Welcome, {name}!")
    menu = st.sidebar.radio("Navigate", ["Threat Analysis", "History", "Logout"])

    if menu == "Threat Analysis":
        st.subheader("📥 Input Threat Intelligence Data")
        user_input = st.text_area(
            "Paste indicators of compromise (IOCs), logs, or any threat-related info:",
            height=300,
            placeholder="[2025-06-21 08:12:33] INFO: User 'alice' logged into system from IP 192.168.0.12\n[2025-06-21 08:22:10] HIGH: Malware detected..."
        )

        analysis_mode = st.radio("Choose Analysis Mode", ["Custom Rules", "Gemini AI"])

        if st.button("Analyze Logs"):
            with st.spinner("Analyzing logs..."):
                if analysis_mode == "Custom Rules":
                    result = custom_rules_analysis(user_input)
                else:
                    result = gemini_threat_analysis(user_input)

            st.success("✅ Threat Analysis Complete!")
            st.markdown(f"✅ Mode: **{analysis_mode}**")
            st.markdown(f"📅 Timestamp: `{datetime.datetime.utcnow().isoformat()} UTC`")
            st.markdown(f"📌 Total Logs Analyzed: {len(user_input.strip().splitlines())}")

            st.subheader("🔍 Threat Intelligence Summary")

            if isinstance(result, str) and '\n' in result:
                st.code(result, language="markdown")
            else:
                st.markdown(result)

    elif menu == "History":
        display_history()

    elif menu == "Logout":
        st.sidebar.info("You have been logged out.")
        st.stop()

elif auth_status is False:
    st.error("❌ Incorrect username or password.")

elif auth_status is None:
    st.warning("Please enter your credentials to continue.")
