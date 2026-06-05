import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
page_title="Pulse Fabric MVP1",
page_icon="🔴",
layout="wide"
)

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
.main {
background-color: #0b0b0b;
}
.block-container {
padding-top: 2rem;
}
h1, h2, h3, h4, p, label {
color: white !important;
}
.metric-card {
background: #1a1a1a;
border: 1px solid #e60000;
border-radius: 16px;
padding: 18px;
color: white;
}
.agent-card {
background: #151515;
border-left: 5px solid #e60000;
border-radius: 12px;
padding: 14px;
margin-bottom: 12px;
color: white;
}
.decision-box {
background: #111111;
border: 1px solid #444;
border-radius: 14px;
padding: 18px;
color: white;
}
.success-box {
background: #102b16;
border: 1px solid #2ecc71;
border-radius: 14px;
padding: 14px;
color: white;
}
.warning-box {
background: #332600;
border: 1px solid #f1c40f;
border-radius: 14px;
padding: 14px;
color: white;
}
.risk-box {
background: #330000;
border: 1px solid #e60000;
border-radius: 14px;
padding: 14px;
color: white;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Sample Requests
# -----------------------------
sample_requests = {
"1 - Eksik Talep / Low Maturity": {
"title": "Customer churn dashboard istiyorum",
"description": "Marketing ekibi için müşteri kaybını gösteren bir dashboard istiyoruz.",
"requester": "Marketing Manager",
"business_goal": "",
"expected_output": "",
"data_owner": "",
"contains_pii": "Unknown",
"urgency": "Medium",
"regulatory_impact": "Unknown"
},
"2 - Yeni Veri Ürünü / Data Product": {
"title": "Customer Churn Prediction Data Product",
"description": "Müşteri kullanım, paket, ödeme, şikayet ve kampanya etkileşim verilerini kullanarak churn prediction modeli için yeni bir veri ürünü oluşturmak istiyoruz.",
"requester": "Data Science Team",
"business_goal": "Churn riskini erken tahmin ederek müşterilere proaktif teklif sunmak",
"expected_output": "ML feature dataset and analytical data product",
"data_owner": "Customer Analytics Domain Owner",
"contains_pii": "Yes",
"urgency": "High",
"regulatory_impact": "Medium"
},
"3 - KVKK / PII Riskli Talep": {
"title": "Campaign Targeting Dataset",
"description": "Kampanya hedefleme için müşteri telefon numarası, TCKN, lokasyon ve paket bilgilerini içeren dataset istiyoruz.",
"requester": "Campaign Operations",
"business_goal": "Müşterilere daha doğru kampanya hedeflemesi yapmak",
"expected_output": "Customer targeting dataset",
"data_owner": "Marketing Data Owner",
"contains_pii": "Yes",
"urgency": "High",
"regulatory_impact": "High"
}
}


# -----------------------------
# Agent Functions
# -----------------------------
def scout_agent(req):
text = (req["title"] + " " + req["description"]).lower()

if "churn" in text or "customer" in text or "müşteri" in text:
domain = "Customer Analytics"
elif "finance" in text or "ifrs" in text:
domain = "Finance"
else:
domain = "Unknown"

if "dashboard" in text:
request_type = "BI / Reporting"
elif "prediction" in text or "ml" in text or "feature" in text:
request_type = "AI / ML Data Product"
elif "telefon" in text or "tckn" in text or "location" in text or "lokasyon" in text:
request_type = "Sensitive Data Access"
else:
request_type = "General Data Request"

return {
"agent": "The Scout",
"role": "Talebi sınıflandırır, domain ve talep tipini bulur.",
"domain": domain,
"request_type": request_type,
"confidence": "91%" if domain != "Unknown" else "58%"
}


def inspector_agent(req):
missing = []

if not req["business_goal"]:
missing.append("Business goal eksik")
if not req["expected_output"]:
missing.append("Expected output eksik")
if not req["data_owner"]:
missing.append("Data owner eksik")
if req["contains_pii"] == "Unknown":
missing.append("PII/KVKK durumu net değil")

score = max(20, 100 - len(missing) * 20)

return {
"agent": "The Inspector",
"role": "Talep olgunluğunu ve eksikleri kontrol eder.",
"maturity_score": score,
"missing_fields": missing,
"status": "PASS" if score >= 70 else "NEEDS CLARIFICATION"
}


def scribe_agent(req, scout, inspector):
brd = f"""
BRD Draft

Request Title:
{req['title']}

Requester:
{req['requester']}

Business Goal:
{req['business_goal'] or '[Missing - should be completed]'}

Expected Output:
{req['expected_output'] or '[Missing - should be completed]'}

Detected Domain:
{scout['domain']}

Detected Request Type:
{scout['request_type']}

Data Owner:
{req['data_owner'] or '[Missing - should be assigned]'}

Initial Acceptance Criteria:
1. Business goal must be confirmed.
2. Data owner must be assigned.
3. PII/KVKK classification must be completed.
4. Metadata and lineage requirements must be documented.
5. Human approval must be captured before next gate.
"""
return {
"agent": "The Scribe",
"role": "BRD ve analiz taslağı üretir.",
"brd": brd
}


def strategist_agent(req, inspector):
score = 50

if req["urgency"] == "High":
score += 20
if req["regulatory_impact"] == "High":
score += 25
elif req["regulatory_impact"] == "Medium":
score += 10
if inspector["maturity_score"] < 70:
score -= 20

score = max(0, min(score, 100))

if score >= 80:
priority = "P1 - High Priority"
elif score >= 60:
priority = "P2 - Medium Priority"
else:
priority = "P3 - Needs Maturity"

return {
"agent": "The Strategist",
"role": "Öncelik skoru ve devam önerisi üretir.",
"priority_score": score,
"priority": priority
}


def guardian_agent(req, scout, inspector):
checks = []
approvals = []

if req["contains_pii"] == "Yes":
checks.append("PII/KVKK data detected")
approvals.append("Governance Lead Approval")
approvals.append("Data Owner Approval")

if scout["request_type"] in ["AI / ML Data Product", "Sensitive Data Access"]:
checks.append("Architecture review required")
approvals.append("Data Architect Approval")

if inspector["maturity_score"] < 70:
checks.append("Request maturity is below threshold")
approvals.append("Requester clarification required")

if not checks:
checks.append("No critical guardrail violation detected")

return {
"agent": "The Guardian",
"role": "Guardrail, KVKK ve onay kontrollerini yapar.",
"checks": checks,
"required_approvals": list(set(approvals)),
"decision": "HUMAN APPROVAL REQUIRED" if approvals else "AUTO PROCEED"
}


def conductor_agent(scout, inspector, strategist, guardian):
if inspector["maturity_score"] < 70:
next_step = "Send back for clarification"
gate_status = "G1 FAILED"
elif guardian["decision"] == "HUMAN APPROVAL REQUIRED":
next_step = "Route to human approval"
gate_status = "G1 CONDITIONAL PASS"
else:
next_step = "Proceed to prioritization"
gate_status = "G1 PASSED"

return {
"agent": "The Conductor",
"role": "Tüm agent çıktılarını birleştirip karar paketi oluşturur.",
"gate_status": gate_status,
"next_step": next_step,
"final_recommendation": next_step
}


# -----------------------------
# UI
# -----------------------------
st.title("🔴 Pulse Fabric MVP1")
st.subheader("AI-Powered Demand Governance Demo")
st.caption("Human Governed. AI Orchestrated.")

col1, col2, col3 = st.columns(3)

with col1:
st.markdown('<div class="metric-card"><h3>26 MD</h3><p>Current manual effort</p></div>', unsafe_allow_html=True)

with col2:
st.markdown('<div class="metric-card"><h3>40–70%</h3><p>Target reduction in request maturation</p></div>', unsafe_allow_html=True)

with col3:
st.markdown('<div class="metric-card"><h3>95%+</h3><p>Target request accuracy</p></div>', unsafe_allow_html=True)

st.divider()

selected = st.selectbox("Select Demo Customer Journey", list(sample_requests.keys()))
request = sample_requests[selected]

left, right = st.columns([1, 1])

with left:
st.header("Incoming Request")

title = st.text_input("Title", request["title"])
description = st.text_area("Description", request["description"], height=150)
requester = st.text_input("Requester", request["requester"])
business_goal = st.text_area("Business Goal", request["business_goal"], height=80)
expected_output = st.text_area("Expected Output", request["expected_output"], height=80)
data_owner = st.text_input("Data Owner", request["data_owner"])

contains_pii = st.selectbox(
"Contains PII?",
["Unknown", "No", "Yes"],
index=["Unknown", "No", "Yes"].index(request["contains_pii"])
)

urgency = st.selectbox(
"Urgency",
["Low", "Medium", "High"],
index=["Low", "Medium", "High"].index(request["urgency"])
)

regulatory_impact = st.selectbox(
"Regulatory Impact",
["Unknown", "Low", "Medium", "High"],
index=["Unknown", "Low", "Medium", "High"].index(request["regulatory_impact"])
)

analyze = st.button("Analyze Request", type="primary")

with right:
st.header("Pulse Fabric Digital Teammates")

st.markdown("""
<div class="agent-card"><b>🧭 The Scout</b><br>Finds domain, owner and request type.</div>
<div class="agent-card"><b>🔍 The Inspector</b><br>Checks maturity, missing fields and request quality.</div>
<div class="agent-card"><b>✍️ The Scribe</b><br>Generates BRD and analysis drafts.</div>
<div class="agent-card"><b>♟️ The Strategist</b><br>Calculates priority and business impact.</div>
<div class="agent-card"><b>🛡️ The Guardian</b><br>Checks guardrails, KVKK and approval needs.</div>
<div class="agent-card"><b>🎼 The Conductor</b><br>Creates the final decision package.</div>
""", unsafe_allow_html=True)


if analyze:
req = {
"title": title,
"description": description,
"requester": requester,
"business_goal": business_goal,
"expected_output": expected_output,
"data_owner": data_owner,
"contains_pii": contains_pii,
"urgency": urgency,
"regulatory_impact": regulatory_impact
}

st.divider()
st.header("Agent Timeline")

with st.spinner("Pulse Fabric is analyzing the request..."):
scout = scout_agent(req)
inspector = inspector_agent(req)
scribe = scribe_agent(req, scout, inspector)
strategist = strategist_agent(req, inspector)
guardian = guardian_agent(req, scout, inspector)
conductor = conductor_agent(scout, inspector, strategist, guardian)

c1, c2, c3 = st.columns(3)

with c1:
st.markdown(f"""
<div class="agent-card">
<h4>🧭 The Scout</h4>
<p><b>Domain:</b> {scout['domain']}</p>
<p><b>Request Type:</b> {scout['request_type']}</p>
<p><b>Confidence:</b> {scout['confidence']}</p>
</div>
""", unsafe_allow_html=True)

with c2:
box_class = "success-box" if inspector["status"] == "PASS" else "warning-box"
st.markdown(f"""
<div class="{box_class}">
<h4>🔍 The Inspector</h4>
<p><b>Maturity Score:</b> {inspector['maturity_score']}/100</p>
<p><b>Status:</b> {inspector['status']}</p>
</div>
""", unsafe_allow_html=True)
if inspector["missing_fields"]:
st.write("Missing fields:")
for item in inspector["missing_fields"]:
st.write(f"- {item}")

with c3:
st.markdown(f"""
<div class="agent-card">
<h4>♟️ The Strategist</h4>
<p><b>Priority Score:</b> {strategist['priority_score']}/100</p>
<p><b>Priority:</b> {strategist['priority']}</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Guardian Check")

guard_class = "risk-box" if guardian["decision"] == "HUMAN APPROVAL REQUIRED" else "success-box"
st.markdown(f"""
<div class="{guard_class}">
<h4>🛡️ The Guardian</h4>
<p><b>Decision:</b> {guardian['decision']}</p>
</div>
""", unsafe_allow_html=True)

st.write("Guardrail checks:")
for check in guardian["checks"]:
st.write(f"- {check}")

if guardian["required_approvals"]:
st.write("Required approvals:")
for approval in guardian["required_approvals"]:
st.write(f"- {approval}")

st.subheader("Generated Documentation")

with st.expander("✍️ BRD Draft generated by The Scribe"):
st.text(scribe["brd"])

st.subheader("Decision Package")

st.markdown(f"""
<div class="decision-box">
<h3>🎼 Final Decision Package</h3>
<p><b>Request:</b> {req['title']}</p>
<p><b>Domain:</b> {scout['domain']}</p>
<p><b>Request Type:</b> {scout['request_type']}</p>
<p><b>Maturity Score:</b> {inspector['maturity_score']}/100</p>
<p><b>Priority:</b> {strategist['priority']}</p>
<p><b>Gate Status:</b> {conductor['gate_status']}</p>
<p><b>Next Step:</b> {conductor['next_step']}</p>
<p><b>Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Human in the Loop")

a1, a2, a3 = st.columns(3)

with a1:
if st.button("Approve"):
st.success("Human approval captured. Request can proceed to next lifecycle state.")

with a2:
if st.button("Send Back"):
st.warning("Request sent back to requester for clarification.")

with a3:
if st.button("Reject"):
st.error("Request rejected due to governance or maturity issues.")

