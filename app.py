import streamlit as st
import joblib
import numpy as np
import requests


st.set_page_config(
    page_title="AI Burnout Recovery Coach",
    page_icon="🧠",
    layout="wide"
)


model = joblib.load("burnout_model.pkl")
scaler = joblib.load("scaler.pkl")

st.markdown("""
<style>
.title {
    font-size: 42px;
    font-weight: 700;
}
.subtitle {
    font-size: 18px;
    color: #555;
    margin-bottom: 30px;
}
.card {
    background-color: #f9f9f9;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}
.success-card {
    background-color: #e8f5e9;
}
.warning-card {
    background-color: #fff3e0;
}
.metric-box {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-size: 22px;
}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="title">AI Study Burnout Detection & Recovery Coach</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Confidence-based burnout analysis with explainable AI & recovery planning</div>',
    unsafe_allow_html=True
)


st.sidebar.header("📊 Daily Study Metrics")

study_hours = st.sidebar.slider("📘 Study Hours", 0.0, 15.0, 5.0, step=0.01)
sleep_hours = st.sidebar.slider("😴 Sleep Hours", 0.0, 12.0, 7.0, step=0.01)
stress_level = st.sidebar.slider("😖 Stress Level (1–5)", 1.0, 5.0, 3.0, step=0.01)
mood_level = st.sidebar.slider("🙂 Mood Level (1–5)", 1.0, 5.0, 3.0, step=0.01)
screen_time = st.sidebar.slider("📱 Screen Time (hours)", 0.0, 12.0, 4.0, step=0.01)

analyze = st.sidebar.button("🚀 Analyze Burnout")


if analyze:
    X = np.array([[study_hours, sleep_hours, stress_level, mood_level, screen_time]])
    X_scaled = scaler.transform(X)

    prediction = model.predict(X_scaled)[0]
    prob = model.predict_proba(X_scaled)[0][1] 

    risk_level = "Not Burnout" if prob < 0.4 else "At Risk"

    col1, col2 = st.columns(2)

  
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
            "Burnout risk is influenced mainly by: "
            + ", ".join(reasons)
            if reasons else
            "Your habits are currently well balanced."
        )

        st.info(explanation)
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("📈 Burnout Risk Trend")

    if "history" not in st.session_state:
        st.session_state.history = []

    st.session_state.history.append(int(prob * 100))
    st.line_chart(st.session_state.history)

    st.subheader("🧘 Recovery Readiness Indicators")

    def status(val, good, bad):
        if val <= good:
            return "🟢 Good"
        elif val <= bad:
            return "🟡 Moderate"
        else:
            return "🔴 Needs Attention"

    st.metric("😴 Sleep", status(7 - sleep_hours, 1, 3))
    st.metric("😖 Stress", status(stress_level, 2, 4))
    st.metric("🙂 Mood", status(5 - mood_level, 1, 3))
    st.metric("📱 Screen", status(screen_time, 4, 7))

    st.subheader("🗓️ Today’s Action Plan")
    st.write("• 📚 Study: 2 focused sessions (25 min)")
    st.write("• ⏸ Breaks: 10-minute walk + hydration")
    st.write("• 😴 Sleep target: 7+ hours")
    st.write("• 📵 Screen cutoff: 30 min before bed")

    webhook_url = "https://hook.relay.app/api/v1/playbook/cmk46ydzq04ei0pm4cmweagct/trigger/rh1N6YEIzOuLz66MQRFLlQ"

    payload = {
        "study_hours": study_hours,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "mood_level": mood_level,
        "screen_time": screen_time,
        "burnout_score": int(prob * 100),
        "risk_level": risk_level
    }

    response = requests.post(webhook_url, json=payload)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🤖 AI Recovery Coach")

        if response.status_code == 200:
          try:
           
            data = response.json()
            st.write(data.get("text", response.text if response.text else "No advice returned"))
          except Exception:
           
            st.write(response.text if response.text else "No advice returned")
        else:
          st.error("Failed to retrieve AI advice")


        st.markdown("</div>", unsafe_allow_html=True)
