%%writefile app.py
import streamlit as st
import joblib
import numpy as np
import requests
import json

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Burnout Recovery Coach",
    page_icon="🧠",
    layout="wide"
)

# ---------------- LOAD MODEL ----------------
model = joblib.load("burnout_model.pkl")
scaler = joblib.load("scaler.pkl")

# ---------------- STYLING ----------------
st.markdown("""
<style>
.title {font-size:42px;font-weight:700;}
.subtitle {font-size:18px;color:#555;margin-bottom:30px;}
.card {background-color:#f9f9f9;padding:25px;border-radius:15px;
box-shadow:0px 4px 12px rgba(0,0,0,0.08);}
.success-card {background-color:#e8f5e9;}
.warning-card {background-color:#fff3e0;}
.metric-box {background-color:#ffffff;padding:15px;border-radius:10px;
text-align:center;font-size:22px;}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="title">AI Study Burnout Detection & Recovery Coach</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI burnout analysis • Smart study planner • Email reminders</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR INPUTS ----------------
st.sidebar.header("📊 Daily Study Metrics")

study_hours = st.sidebar.slider("📘 Study Hours", 0.0, 15.0, 5.0)
sleep_hours = st.sidebar.slider("😴 Sleep Hours", 0.0, 12.0, 7.0)
stress_level = st.sidebar.slider("😖 Stress Level", 1.0, 5.0, 3.0)
stress_level_int = int(round(stress_level))
mood_level = st.sidebar.slider("🙂 Mood Level", 1.0, 5.0, 3.0)
screen_time = st.sidebar.slider("📱 Screen Time", 0.0, 12.0, 4.0)

analyze = st.sidebar.button("🚀 Analyze Burnout")

# ---------------- MAIN LOGIC ----------------
if analyze:

    # ---------------- PREDICTION ----------------
    X = np.array([[study_hours, sleep_hours, stress_level, mood_level, screen_time]])
    X_scaled = scaler.transform(X)
    prob = model.predict_proba(X_scaled)[0][1]
    risk_level = "Not Burnout" if prob < 0.4 else "At Risk"

    col1, col2 = st.columns(2)

    # ---------------- LEFT PANEL ----------------
    with col1:

        if prob < 0.4:
            st.markdown('<div class="card success-card">', unsafe_allow_html=True)
            st.subheader("✅ Burnout Risk Status")
        else:
            st.markdown('<div class="card warning-card">', unsafe_allow_html=True)
            st.subheader("⚠️ Burnout Risk Status")

        st.markdown(
            f'<div class="metric-box">Burnout Risk Score<br><b>{int(prob*100)}%</b></div>',
            unsafe_allow_html=True
        )
        st.write(f"**Status:** {risk_level}")

        reasons = []
        if sleep_hours < 6: reasons.append("low sleep")
        if study_hours > 7: reasons.append("high study load")
        if stress_level > 3: reasons.append("high stress")
        if mood_level < 3: reasons.append("low mood")
        if screen_time > 6: reasons.append("excessive screen time")

        explanation = (
            "Burnout risk influenced by: " + ", ".join(reasons)
            if reasons else "Your habits are currently balanced."
        )
        st.info(explanation)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- RELAY WEBHOOK ----------------
    webhook_url = "https://hook.relay.app/api/v1/playbook/cmm29hss802ml0oku1w0r6fqr/trigger/e2kByZFPIM3OQgYZa2weRQ"

    # Structured payload for Relay (pass numeric values explicitly)
    payload = {
        "user_data": {
            "study_hours": study_hours,
            "sleep_hours": sleep_hours,
            "stress_level": stress_level,
            "mood_level": mood_level,
            "screen_time": screen_time
        }
    }

    # ---------------- CALL RELAY ----------------
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        data = response.json()
        if isinstance(data, dict) and "body" in data:
            data = data["body"]

        # Ensure numeric fields are numbers
        if isinstance(data, dict):
            if "burnout_level" in data:
                data["burnout_level"] = int(data["burnout_level"])
            if "burnout_score" in data:
                data["burnout_score"] = int(data["burnout_score"])

    except Exception as e:
        data = {}
        st.error(f"Relay error: {e}")

    # ---------------- RIGHT PANEL ----------------
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🤖 AI Recovery Coach")

        if isinstance(data, dict):
            if "advise" in data:
                st.write("### 🧠 Advice")
                st.write(data["advise"])

            if "study_plan" in data and isinstance(data["study_plan"], list):
                st.write("### 📅 Study Plan")
                for item in data["study_plan"]:
                    time = item.get("time", "")
                    task = item.get("task", "")
                    st.write(f"• {time} → {task}")

            if "motivation" in data:
                st.write("### 💬 Motivation")
                st.info(data["motivation"])

            if "action" in data:
                st.write(f"**Action:** {data['action']}")

        if not data:
            st.warning("No valid response from Relay.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- TREND GRAPH ----------------
    st.subheader("📈 Burnout Risk Trend")
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append(int(prob*100))
    st.line_chart(st.session_state.history)
