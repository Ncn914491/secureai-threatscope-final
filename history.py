# history.py
import streamlit as st
import pandas as pd
import os

HISTORY_FILE = "analysis_history.csv"

def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    else:
        return pd.DataFrame(columns=["Timestamp", "Input Data", "Analysis Type", "Result"])

def display_history():
    st.subheader("📜 Threat Analysis History")
    history_df = load_history()

    if history_df.empty:
        st.info("No analysis history available.")
    else:
        # Add search/filter functionality
        search = st.text_input("Search by keyword:")
        if search:
            filtered_df = history_df[
                history_df["Input Data"].str.contains(search, case=False, na=False)
                | history_df["Analysis Type"].str.contains(search, case=False, na=False)
                | history_df["Result"].str.contains(search, case=False, na=False)
            ]
        else:
            filtered_df = history_df

        st.dataframe(filtered_df, use_container_width=True)

        # Option to download as CSV
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download CSV",
            data=csv,
            file_name="threat_analysis_history.csv",
            mime="text/csv"
        )
