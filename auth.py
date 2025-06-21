import streamlit as st
import streamlit_authenticator as stauth

# Dummy credentials
def login():
    # --- Define credentials dictionary ---
    usernames = ['secureai']
    names = ['SecureAI User']
    passwords = ['secureai']

    hashed_passwords = stauth.Hasher(passwords).generate()

    credentials = {
        "usernames": {
            usernames[0]: {
                "name": names[0],
                "password": hashed_passwords[0]
            }
        }
    }

    # --- Create the authenticator instance ---
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name='secureai_app',
        key='abcdef',
        cookie_expiry_days=1
    )

    name, auth_status, username = authenticator.login("🔐 SecureAI Login", "main")

    if auth_status is False:
        st.error("Invalid username or password.")
    elif auth_status is None:
        st.warning("Please enter your credentials.")

    return auth_status, authenticator, name
