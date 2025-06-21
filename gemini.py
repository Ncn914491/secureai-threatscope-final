from vertexai.preview.generative_models import GenerativeModel

def gemini_threat_analysis(logs: str):
    if not logs.strip():
        return "No logs provided for analysis by Gemini model."

    model = GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
You are a cybersecurity analyst AI assistant.

Analyze the following threat intelligence logs and:
- Identify any critical threats or suspicious behavior.
- Classify the events based on severity.
- Suggest recommended actions or mitigations.
- Provide a concise summary for reporting.

Logs:
{logs}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "No response received from Gemini model."
    except Exception as e:
        return f"Error during Gemini threat analysis: {e}"

