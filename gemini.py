import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold
import os

# Configuration for Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")  # Your Google Cloud Project ID
LOCATION = os.environ.get("GCP_REGION", "us-central1")    # Your Google Cloud Region (e.g., "us-central1")
MODEL_NAME = "gemini-1.5-flash-001" # Updated model name

def init_vertex_ai():
    """Initializes Vertex AI SDK with project and location."""
    try:
        if not PROJECT_ID:
            st.error("GCP_PROJECT_ID environment variable not set. Vertex AI features will be unavailable.")
            return False
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        return True
    except Exception as e:
        st.error(f"Error initializing Vertex AI: {e}. Ensure your GCP project and location are correct and you have authenticated.")
        return False

# Call initialization once when the script loads
vertex_ai_initialized = init_vertex_ai()

def gemini_threat_analysis(logs: str):
    """
    Analyzes threat intelligence logs using the Gemini model via Vertex AI.
    """
    if not vertex_ai_initialized:
        return "Vertex AI SDK not initialized. Cannot perform analysis."

    if not logs.strip():
        return "No logs provided for analysis by Gemini model."

    try:
        model = GenerativeModel(MODEL_NAME)
    except Exception as e:
        return f"Error loading Gemini model ({MODEL_NAME}): {e}. Ensure the model is available in {LOCATION} and you have permissions."

    prompt = f"""
You are a highly skilled cybersecurity analyst AI assistant. Your task is to meticulously analyze the provided threat intelligence data.

**Instructions:**
1.  **Identify Critical Threats:** Pinpoint any events, patterns, or indicators that suggest immediate or significant risk (e.g., active intrusions, malware execution, data exfiltration attempts).
2.  **Detect Suspicious Behavior:** Highlight any activities that deviate from normal patterns or could be precursors to an attack (e.g., unusual login attempts, port scanning, policy violations).
3.  **Classify by Severity:** Categorize identified threats and suspicious behaviors using a clear severity scale (e.g., Critical, High, Medium, Low, Informational). Provide justification for each classification.
4.  **Recommend Actions/Mitigations:** For each identified item, suggest concrete, actionable steps for response, remediation, or further investigation.
5.  **Provide Concise Summary:** Generate a brief executive summary of the overall threat landscape based on the logs.

**Threat Intelligence Logs:**
```
{logs}
```

**Output Format:**
Please structure your analysis clearly, using Markdown for readability. For example:

### Threat Analysis Report

**Executive Summary:**
(Brief overview of findings)

---

**Detailed Findings:**

**1. Threat/Behavior:** (Description)
    *   **Severity:** (Critical/High/Medium/Low/Informational)
    *   **Justification:** (Why this severity)
    *   **Details/Evidence:** (Specific log lines or patterns)
    *   **Recommended Actions:**
        *   (Action 1)
        *   (Action 2)

**2. Threat/Behavior:** (Description)
    *   **Severity:** (Critical/High/Medium/Low/Informational)
    *   **Justification:** (Why this severity)
    *   **Details/Evidence:** (Specific log lines or patterns)
    *   **Recommended Actions:**
        *   (Action 1)
        *   (Action 2)

---
(Continue for all findings)
"""

    generation_config = {
        "max_output_tokens": 8192, # Increased for potentially detailed reports
        "temperature": 0.2, # Lower temperature for more factual, less creative responses
        "top_p": 0.95,
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    try:
        response = model.generate_content(
            [prompt],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )
        if response and response.candidates:
            # Accessing text from the first candidate's content part
            if response.candidates[0].content.parts and response.candidates[0].content.parts[0].text:
                 return response.candidates[0].content.parts[0].text.strip()
            else:
                return "Gemini model returned an empty response part."
        else:
            # Log the full response if it's not as expected for debugging
            st.warning(f"Unexpected response structure from Gemini: {response}")
            return "No valid response received from Gemini model or response format is unexpected."
    except vertexai.generative_models._generative_models.BlockedBySafetySettingException as e:
        st.error(f"Gemini threat analysis blocked by safety settings: {e}")
        return f"Analysis blocked by safety settings. Please review the input or adjust safety configurations if appropriate. Details: {e}"
    except Exception as e:
        st.error(f"Error during Gemini threat analysis: {e}")
        # More detailed error logging for debugging
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return f"An unexpected error occurred during Gemini threat analysis: {e}"

