import streamlit as st
from datetime import datetime

def analyze_threats():
    st.subheader("📥 Input Threat Intelligence Data")
    threat_data = st.text_area("Paste indicators of compromise (IOCs), logs, or any threat-related info:", height=300)

    analysis_type = st.selectbox("Choose Analysis Mode", ["Basic Scan", "Deep Dive", "Custom Rules"])

    if st.button("Analyze"):
        if not threat_data.strip():
            st.warning("Please provide threat logs to analyze.")
            return

        st.spinner("Analyzing...")

        # Parse lines
        lines = threat_data.strip().split("\n")
        total_logs = len(lines)
        severity_count = {"INFO": 0, "WARNING": 0, "CRITICAL": 0, "HIGH": 0}
        critical_events = []

        for line in lines:
            for sev in severity_count:
                if sev in line:
                    severity_count[sev] += 1
            if any(keyword in line for keyword in ["Malware", "Port Scan", "Trojan", "Exploit", "SQL Injection"]):
                critical_events.append(line)

        # Results
        st.success("✅ Threat Analysis Complete!")
        st.write(f"✅ Mode: {analysis_type}")
        st.write(f"📅 Timestamp: {datetime.utcnow().isoformat()} UTC")
        st.write(f"📌 Total Logs Analyzed: {total_logs}")
        st.write("")

        st.subheader("📊 Severity Breakdown")
        for sev, count in severity_count.items():
            st.write(f"🔸 {sev}: {count}")

        st.subheader("🚨 Critical Findings")
        if critical_events:
            for event in critical_events:
                st.error(event)
        else:
            st.info("No critical threats detected in current input.")

        # Optional: Save to history (you can improve this further)
        if "history" not in st.session_state:
            st.session_state["history"] = []
        st.session_state["history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "input": threat_data,
            "mode": analysis_type,
            "critical_findings": critical_events,
            "severity_summary": severity_count
        })
    else:
        st.info("Submit logs to begin analysis.")
