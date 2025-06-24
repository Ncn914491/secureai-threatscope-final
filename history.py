import streamlit as st
import pandas as pd
from google.cloud import storage
import io
import os # Still used for environment variable

# Configuration for GCS
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME") # Configure via env variable
HISTORY_FILE_BLOB_NAME = "analysis_history.csv"

def get_gcs_client():
    """Initializes and returns a GCS client."""
    try:
        client = storage.Client()
        return client
    except Exception as e:
        st.error(f"Failed to connect to Google Cloud Storage: {e}. Ensure credentials are set up.")
        return None

def load_history_from_gcs():
    """Loads the analysis history from GCS."""
    if not BUCKET_NAME:
        st.error("GCS_BUCKET_NAME environment variable not set.")
        return pd.DataFrame(columns=["Timestamp", "Input Data", "Analysis Type", "Result"])

    client = get_gcs_client()
    if not client:
        return pd.DataFrame(columns=["Timestamp", "Input Data", "Analysis Type", "Result"])

    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(HISTORY_FILE_BLOB_NAME)

    try:
        if blob.exists():
            csv_data = blob.download_as_bytes()
            df = pd.read_csv(io.BytesIO(csv_data))
            return df
        else:
            # If the file doesn't exist, return an empty DataFrame with correct columns
            return pd.DataFrame(columns=["Timestamp", "Input Data", "Analysis Type", "Result"])
    except Exception as e:
        st.error(f"Error loading history from GCS: {e}")
        return pd.DataFrame(columns=["Timestamp", "Input Data", "Analysis Type", "Result"])

def save_history_to_gcs(new_entry_df):
    """Appends a new entry to the history CSV in GCS."""
    if not BUCKET_NAME:
        st.error("GCS_BUCKET_NAME environment variable not set. Cannot save history.")
        return False

    client = get_gcs_client()
    if not client:
        return False

    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(HISTORY_FILE_BLOB_NAME)

    try:
        if blob.exists():
            existing_df = load_history_from_gcs()
            # Ensure columns match before concatenating, especially if existing_df was empty
            if existing_df.empty and not new_entry_df.empty:
                 # If existing is empty, new_entry_df becomes the history
                updated_df = new_entry_df
            elif not new_entry_df.empty:
                 updated_df = pd.concat([existing_df, new_entry_df], ignore_index=True)
            else: # new_entry_df is empty, no change
                updated_df = existing_df
        else:
            updated_df = new_entry_df

        if not updated_df.empty:
            csv_buffer = io.StringIO()
            updated_df.to_csv(csv_buffer, index=False)
            blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")
            csv_buffer.close()
            return True
        return False # Nothing to save
    except Exception as e:
        st.error(f"Error saving history to GCS: {e}")
        return False


def display_history():
    st.subheader("📜 Threat Analysis History (Stored in GCS)")

    if not BUCKET_NAME:
        st.warning("Google Cloud Storage bucket name (GCS_BUCKET_NAME) is not configured. History feature is limited.")
        # Optionally, provide a way to download a local copy if one exists or was just generated
        # For now, we just show a warning.
        if os.path.exists("analysis_history.csv"): # Fallback for local if GCS not set
             st.info("Displaying local fallback 'analysis_history.csv'. This will not persist across sessions if GCS is not configured.")
             history_df = pd.read_csv("analysis_history.csv")
        else:
            history_df = pd.DataFrame(columns=["Timestamp", "Input Data", "Analysis Type", "Result"])

    else:
        with st.spinner("Loading history from GCS..."):
            history_df = load_history_from_gcs()

    if history_df.empty:
        st.info("No analysis history available.")
    else:
        search = st.text_input("Search by keyword:")
        if search:
            # Ensure all columns are string type for robust searching
            search_df = history_df.astype(str)
            filtered_df = history_df[
                search_df.apply(lambda row: row.str.contains(search, case=False, na=False).any(), axis=1)
            ]
        else:
            filtered_df = history_df

        st.dataframe(filtered_df, use_container_width=True)

        if not filtered_df.empty:
            csv_export = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Displayed History as CSV",
                data=csv_export,
                file_name="displayed_threat_analysis_history.csv",
                mime="text/csv",
            )

# Example function to be called after an analysis to save it
# This function would be called from secureai_streamlit.py
def record_analysis_in_history(timestamp, input_data, analysis_type, result):
    """Records a single analysis event to GCS."""
    new_entry = {
        "Timestamp": [timestamp],
        "Input Data": [input_data],
        "Analysis Type": [analysis_type],
        "Result": [str(result)] # Ensure result is string
    }
    new_entry_df = pd.DataFrame(new_entry)

    if not BUCKET_NAME:
        st.warning("GCS_BUCKET_NAME not set. Saving history locally to 'analysis_history.csv' as a fallback.")
        # Fallback to local CSV if GCS is not configured
        if os.path.exists("analysis_history.csv"):
            existing_df = pd.read_csv("analysis_history.csv")
            updated_df = pd.concat([existing_df, new_entry_df], ignore_index=True)
        else:
            updated_df = new_entry_df
        updated_df.to_csv("analysis_history.csv", index=False)
        st.sidebar.info("History saved locally (fallback).")
        return

    if save_history_to_gcs(new_entry_df):
        st.sidebar.info("Analysis recorded in GCS history.")
    else:
        st.sidebar.error("Failed to record analysis in GCS history.")
