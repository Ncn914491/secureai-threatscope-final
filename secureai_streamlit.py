import streamlit as st
import datetime
from auth import login_page, logout
from history import display_history, record_analysis_in_history # Added record_analysis_in_history
from rules import custom_rules_analysis
from gemini import gemini_threat_analysis

# Set page config
st.set_page_config(page_title="SecureAI ThreatScope", layout="wide")
st.markdown("## 🛡️ SecureAI ThreatScope")

# Initialize session state for authentication if not already done
if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# Authenticate user
# The login_page function now handles the display of login UI and returns status
if not st.session_state["auth_status"]:
    auth_status, user_name, user_email = login_page()
    if not auth_status: # If still not authenticated, stop further rendering of main app
        st.stop()
else: # User is authenticated
    user_name = st.session_state["user_name"]


# Main application content if authenticated
st.sidebar.success(f"Welcome, {user_name}!")
menu_options = ["Threat Analysis", "History"]
if st.session_state.get("auth_status"): # Show logout only if logged in
    menu_options.append("Logout")

menu = st.sidebar.radio("Navigate", menu_options)


if menu == "Threat Analysis":
    st.subheader("📥 Input Threat Intelligence Data")
    user_input = st.text_area(
        "Paste indicators of compromise (IOCs), logs, or any threat-related info:",
        height=300,
        placeholder="[2025-06-21 08:12:33] INFO: User 'alice' logged into system from IP 192.168.0.12\n[2025-06-21 08:22:10] HIGH: Malware detected..."
    )

    analysis_mode = st.radio("Choose Analysis Mode", ["Custom Rules", "Gemini AI"])

    if st.button("Analyze Logs"):
        if not user_input.strip():
            st.warning("Please input data for analysis.")
        else:
            with st.spinner("Analyzing logs..."):
                if analysis_mode == "Custom Rules":
                    result = custom_rules_analysis(user_input)
                else: # Gemini AI
                    result = gemini_threat_analysis(user_input)

            current_timestamp = datetime.datetime.utcnow().isoformat()
            # Record the analysis in history
            record_analysis_in_history(
                timestamp=current_timestamp,
                input_data=user_input,
                analysis_type=analysis_mode,
                result=str(result) # Ensure result is stored as a string
            )

            st.success("✅ Threat Analysis Complete!")
            st.markdown(f"✅ Mode: **{analysis_mode}**")
            # Display the same timestamp that was recorded
            st.markdown(f"📅 Timestamp: `{current_timestamp} UTC`")
            st.markdown(f"📌 Total Logs Analyzed: {len(user_input.strip().splitlines())}")

            st.subheader("🔍 Threat Intelligence Summary")

            if isinstance(result, str) and '\n' in result: # Check if result is multiline string
                st.code(result, language="markdown")
            else:
                st.markdown(str(result)) # Ensure result is always a string for markdown

elif menu == "History":
    display_history()

elif menu == "Logout":
    logout() # Call the logout function from auth.py
    # The logout function itself will call st.rerun()
