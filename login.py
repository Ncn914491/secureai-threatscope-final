import streamlit_authenticator as stauth
import streamlit as st

def login():
    names = ["SecureAI"]
    usernames = ["secureai"]
    passwords = ["secureai"]  # plaintext password

    hashed_passwords = stauth.Hasher(passwords).generate()

    credentials = {
        "usernames": {
            usernames[0]: {
                "name": names[0],
                "password": hashed_passwords[0]
            }
        }
    }

    authenticator = stauth.Authenticate(
        credentials,
        "secureai_login",   # cookie name
        "secureai_key",     # signature key
        cookie_expiry_days=1
    )

    name, auth_status, _ = authenticator.login("🔐 Login", "main")

    return auth_status, authenticator, name
