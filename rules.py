from datetime import datetime

def custom_rules_analysis(logs: str):
    lines = logs.strip().split("\n")
    if not lines:
        return "No input provided.", [], {}

    critical_findings = []
    severity_count = {"INFO": 0, "WARNING": 0, "HIGH": 0, "CRITICAL": 0}

    for line in lines:
        if any(sev in line for sev in severity_count):
            for severity in severity_count:
                if severity in line:
                    severity_count[severity] += 1
                    if severity in ["HIGH", "CRITICAL"]:
                        critical_findings.append(line)
                    break

    summary = f"""
✅ Threat Analysis Complete!

✅ Mode: Custom Rules

📅 Timestamp: {datetime.utcnow().isoformat()} UTC

📌 Total Logs Analyzed: {len(lines)}

📊 Severity Breakdown
🔸 INFO: {severity_count['INFO']}
🔸 WARNING: {severity_count['WARNING']}
🔸 CRITICAL: {severity_count['CRITICAL']}
🔸 HIGH: {severity_count['HIGH']}

🚨 Critical Findings
"""
    for finding in critical_findings:
        summary += f"{finding}\n"

    return summary.strip(), critical_findings, severity_count
