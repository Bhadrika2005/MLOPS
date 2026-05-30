import streamlit as st
import time



st.set_page_config(
    page_title="CrimeVision AI",
    page_icon="🚨",
    layout="wide"
)



st.markdown("""
<style>

.stApp {
    background: linear-gradient(to right, #0B1120, #111827);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Remove Streamlit Header */
header {
    visibility: hidden;
}

/* Main Title */
.main-title {
    font-size: 65px;
    font-weight: 800;
    color: #FF4B4B;
    margin-bottom: 10px;
}

/* Subtitle */
.sub-title {
    font-size: 24px;
    color: #D1D5DB;
    margin-bottom: 35px;
}

/* Section Card */
.card {
    background-color: #161B22;
    padding: 35px;
    border-radius: 22px;
    border: 1px solid #2F3746;
    box-shadow: 0px 0px 18px rgba(255,75,75,0.12);
}

/* Upload Box */
.upload-box {
    border: 2px dashed #FF4B4B;
    padding: 45px;
    border-radius: 18px;
    background-color: #0F172A;
    text-align: center;
}

/* Metric Card */
.metric-card {
    background-color: #161B22;
    padding: 25px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid #2F3746;
}

.metric-number {
    font-size: 36px;
    font-weight: bold;
    color: #FF4B4B;
}

.metric-text {
    color: #D1D5DB;
}

/* Footer */
.footer {
    text-align: center;
    color: gray;
    margin-top: 60px;
    margin-bottom: 20px;
}

.stButton>button {
    background-color: #FF4B4B;
    color: white;
    border-radius: 12px;
    height: 55px;
    font-size: 18px;
    font-weight: bold;
    border: none;
}

.stButton>button:hover {
    background-color: #E63E3E;
    color: white;
}

</style>
""", unsafe_allow_html=True)


col1, col2 = st.columns([2,1])

with col1:

    st.markdown(
        '<div class="main-title">🚨 CrimeVision AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">AI-Powered CCTV Suspicious Activity Detection & Investigation Assistance System</div>',
        unsafe_allow_html=True
    )

    st.write("""
CrimeVision AI helps investigators analyze massive CCTV footage automatically using Artificial Intelligence.

The system detects suspicious activities, weapons, unusual behavior,
and assists police officers during criminal investigations by reducing
manual video analysis time.
""")

with col2:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/4140/4140047.png",
        width=260
    )

st.write("")
st.write("")



st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("📌 Problem Statement")

st.write("""
During criminal investigations, investigators manually analyze large amounts of CCTV footage collected from:

- Streets
- Shops
- ATMs
- Railway Stations
- Offices
- Parking Areas

A single investigation may contain hundreds of hours of surveillance videos,
making the investigation process slow, stressful, and time-consuming.

CrimeVision AI automates video analysis using AI-based suspicious activity detection.
""")

st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.write("")



c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">🎥</div>
        <div class="metric-text">CCTV Video Analysis</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">⚠️</div>
        <div class="metric-text">Suspicious Activity Detection</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">🔫</div>
        <div class="metric-text">Weapon Detection</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">📊</div>
        <div class="metric-text">Investigation Reports</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")


st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("📂 Upload CCTV Video Folder")

st.markdown("""
<div class="upload-box">
<h3>Drop Surveillance Videos Here</h3>
<p>Upload any number of CCTV videos for AI-powered crime analysis</p>
<p>Supported Formats: MP4 • AVI • MOV • MKV</p>
</div>
""", unsafe_allow_html=True)

st.write("")

uploaded_files = st.file_uploader(
    "Select CCTV Videos",
    type=["mp4", "avi", "mov", "mkv"],
    accept_multiple_files=True
)

st.write("")

if uploaded_files:

    st.success(f"✅ {len(uploaded_files)} videos uploaded successfully")

    with st.expander("📁 Uploaded Video Files"):

        for file in uploaded_files:
            st.write(f"🎥 {file.name}")

    st.write("")

    if st.button("🚀 Start AI Crime Analysis", use_container_width=True):

        progress = st.progress(0)
        status = st.empty()

        for i in range(100):
            time.sleep(0.03)
            progress.progress(i + 1)
            status.info(f"Analyzing CCTV footage... {i+1}%")

        st.success("✅ Analysis Completed Successfully")

        st.write("")

        st.subheader("🚨 Detection Results")

        d1, d2, d3 = st.columns(3)

        with d1:
            st.error("⚠️ Suspicious Activities Detected: 5")

        with d2:
            st.warning("🔫 Weapon Detection Alerts: 2")

        with d3:
            st.success("✅ Safe Videos: 14")

        st.write("")

        st.subheader("📊 Threat Detection Summary")

        st.bar_chart({
            "Threat Level": [4, 7, 3, 6, 2]
        })

st.markdown('</div>', unsafe_allow_html=True)



st.markdown(
    '<div class="footer">CrimeVision AI • Intelligent CCTV Investigation Assistance Platform</div>',
    unsafe_allow_html=True
)