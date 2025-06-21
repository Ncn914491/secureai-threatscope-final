import streamlit as st

def login():
    # Page Setup
    st.set_page_config(page_title="SecureAI Login", layout="centered")
    st.title("🔐 SecureAI Login")

    # Credential Input
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Login Trigger
    if st.button("Login"):
        if username == "secureai" and password == "secureai":
            st.success("✅ Login successful")
            st.session_state["authenticated"] = True
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")

    # Prevent further rendering if not authenticated
    st.stop()
