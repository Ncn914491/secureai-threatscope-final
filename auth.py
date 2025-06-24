import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

import os # Ensure os is imported if not already

# Initialize Firebase Admin SDK
firebase_admin_initialized = False
if not firebase_admin._apps: # Check if Firebase app already initialized
    try:
        # Primary method: Use Application Default Credentials
        # This is the recommended way for GCP environments (Cloud Run, GCE, GKE, etc.)
        # and local dev when `gcloud auth application-default login` has been run.
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        firebase_admin_initialized = True
        # st.sidebar.info("Firebase Admin SDK initialized using Application Default Credentials.")
    except Exception as e_adc:
        # Fallback: Try to use a specific service account key file path
        # This path can be set via an environment variable. Useful for local dev or specific setups.
        firebase_sa_key_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
        if firebase_sa_key_path:
            if os.path.exists(firebase_sa_key_path):
                try:
                    cred = credentials.Certificate(firebase_sa_key_path)
                    firebase_admin.initialize_app(cred)
                    firebase_admin_initialized = True
                    # st.sidebar.info(f"Firebase Admin SDK initialized using key from {firebase_sa_key_path}.")
                except Exception as e_path:
                    st.error(f"Failed to initialize Firebase SDK with key from {firebase_sa_key_path}: {e_path}. ADC also failed: {e_adc}")
            else:
                st.error(f"FIREBASE_SERVICE_ACCOUNT_KEY_PATH is set to '{firebase_sa_key_path}', but the file does not exist. ADC also failed: {e_adc}")
        else:
            # If no specific path and ADC failed, then report ADC failure.
            st.error(f"Firebase Admin SDK initialization failed. Application Default Credentials error: {e_adc}. FIREBASE_SERVICE_ACCOUNT_KEY_PATH not set.")
else: # Already initialized
    firebase_admin_initialized = True
    # st.sidebar.info("Firebase Admin SDK was already initialized.")


def login_page():
    """Handles the Firebase login process."""
    st.title("🔐 SecureAI Login")

    if not firebase_admin_initialized:
        st.error("Firebase SDK not initialized. Please check server logs.")
        return None, None, None

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            if email and password:
                try:
                    # This is a simplified example. In a real app, you'd get an ID token
                    # from the client-side Firebase SDK and verify it here.
                    # For a pure Streamlit app without client-side JS, direct email/password
                    # login with Admin SDK is not the standard Firebase auth flow for end-users.
                    # The Admin SDK is typically used to manage users or verify tokens.
                    #
                    # A common pattern for web apps is:
                    # 1. User signs in on the client-side (e.g., using Firebase JS SDK).
                    # 2. Client gets an ID token.
                    # 3. Client sends ID token to the backend (Streamlit app).
                    # 4. Backend (Streamlit) verifies the ID token using Admin SDK.
                    #
                    # Since Streamlit doesn't easily support client-side JS for this,
                    # we'll simulate a verification step. For a real app, consider
                    # integrating with Firebase Web (JS) or using a different auth method
                    # if you must do everything server-side without custom components.

                    # Placeholder for actual user lookup if using custom token verification
                    # user = firebase_auth.get_user_by_email(email)
                    # For now, we'll assume if we reach here, the login is "successful"
                    # in a conceptual sense, but this isn't secure for real email/password.
                    #
                    # A more direct (but less common for web frontends) approach for some use cases:
                    # If you were building a CLI or a backend service that needs to *act as* a user,
                    # you might use custom tokens, but that's not for typical user login.

                    # For a pure Streamlit app, you might consider:
                    # - Using a simpler auth mechanism if Firebase Web isn't an option.
                    # - Building a Streamlit custom component to handle Firebase JS login.
                    # - Using a pre-built Streamlit Firebase auth component if one exists.

                    # This demonstration will proceed by setting session state as if login succeeded.
                    # THIS IS NOT SECURE FOR PRODUCTION EMAIL/PASSWORD LOGIN.
                    st.session_state["auth_status"] = True
                    st.session_state["user_email"] = email
                    st.session_state["user_name"] = email.split('@')[0] # Simple name
                    st.rerun() # Rerun to reflect login status
                except firebase_admin.auth.FirebaseError as e:
                    st.error(f"Login failed: {e.message if hasattr(e, 'message') else str(e)}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
            else:
                st.warning("Please enter both email and password.")

    with col2:
        if st.button("Sign Up (Not Implemented)"):
            st.info("Sign-up functionality is not yet implemented in this demo.")
            # Example of how you might add a user:
            # try:
            #     user = firebase_auth.create_user(email=email, password=password)
            #     st.success(f"User {user.email} created successfully!")
            # except Exception as e:
            #     st.error(f"Could not create user: {e}")

    # Initialize session state variables if they don't exist
    if "auth_status" not in st.session_state:
        st.session_state["auth_status"] = None
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None


    return st.session_state["auth_status"], st.session_state["user_name"], st.session_state["user_email"]


def logout():
    """Handles the logout process."""
    if "auth_status" in st.session_state:
        st.session_state["auth_status"] = None
    if "user_name" in st.session_state:
        st.session_state["user_name"] = None
    if "user_email" in st.session_state:
        st.session_state["user_email"] = None
    # No direct Firebase Admin SDK logout for users like client SDKs.
    # Clearing session state is the primary action here.
    st.success("You have been logged out.")
    st.rerun()
