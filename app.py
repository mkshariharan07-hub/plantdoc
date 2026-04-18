"""
app.py — PlantPulse AI + Quantum  (Enhanced v2)
=================================================
Auto-detects whether the loaded model uses raw pixels (49152) or
histogram features (63) and extracts accordingly — no retraining needed
for the app to work. Retrain with main.py for best accuracy.
"""

import sys
import streamlit as st
import cv2
import numpy as np
import joblib
import os
import json
import datetime
import requests
from dotenv import load_dotenv

# Load environment variables at the very beginning
load_dotenv()

# Force UTF-8 encoding for standard output to avoid Windows console errors with emojis
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Shared utilities — single source of truth for features & prediction
from utils import (
    predict_image, 
    get_disease_info,
    FALLBACK_INFO,
    get_feature_mode, 
    load_model_and_scaler,
    decode_bytes_to_bgr, 
    build_quantum_circuit,
    run_quantum,
    extract_features,
    FEATURE_DIM,
    identify_plant_plantnet,
    identify_crop_health,
    get_perenual_care_info,
    calculate_quantum_risk,
    get_remedy_purchase_links,
    generate_pdf_report,
    simulate_environment,
    FEATURE_MODE_RAW, 
    FEATURE_MODE_HIST
)

# ===============================
# PAGE CONFIG & STYLING
# ===============================
st.set_page_config(
    page_title="PlantPulse AI + Quantum",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Outfit:wght@300;400;600;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

    /* Animated Cinematic Background */
    .main { 
        background: radial-gradient(circle at top right, #1a2935 0%, #0f172a 40%, #020617 100%); 
        background-size: 200% 200%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Ultra-Premium Super Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
        color: white; border: none; border-radius: 16px;
        padding: 0.8rem 1.5rem; font-weight: 800; font-size: 1.05rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4), inset 0 2px 4px rgba(255,255,255,0.2);
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    .stButton>button:hover { 
        transform: translateY(-5px) scale(1.03); 
        box-shadow: 0 15px 35px rgba(16, 185, 129, 0.6), inset 0 2px 4px rgba(255,255,255,0.3); 
        filter: brightness(1.1);
    }
    .stButton>button:active { transform: translateY(0px) scale(0.98); }

    /* Ultra Glassmorphism Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        border-left: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px; padding: 2rem;
        text-align: center; 
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: ""; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%);
        opacity: 0; transition: opacity 0.4s ease;
        pointer-events: none;
    }
    .metric-card:hover::before { opacity: 1; }
    .metric-card:hover { 
        transform: translateY(-8px); 
        border-color: rgba(16, 185, 129, 0.5);
        box-shadow: 0 15px 45px rgba(16, 185, 129, 0.25);
    }
    .metric-card h4 { color: #94a3b8; font-weight: 600; letter-spacing: 2px; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 0.5rem; }
    .metric-card h2 { color: #f8fafc; font-weight: 900; font-size: 2.2rem; margin: 0; background: linear-gradient(90deg, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

    /* Interactive Commerce Links */
    .purchase-button {
        display: flex; align-items: center; justify-content: flex-start; gap: 12px;
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 14px 20px;
        text-decoration: none; color: #f8fafc !important;
        font-weight: 600; font-size: 0.95rem;
        margin-bottom: 12px; transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .purchase-button:hover {
        background: linear-gradient(135deg, rgba(16,185,129,0.9), rgba(5,150,105,0.9));
        border-color: #34d399;
        transform: scale(1.03) translateX(8px);
        box-shadow: 0 10px 25px rgba(16,185,129,0.4);
    }

    /* Badges with Neon Pulse Glow */
    .quantum-badge {
        background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
        color: white; padding: 6px 18px; border-radius: 50px;
        font-size: 0.85rem; font-weight: 800;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4);
        text-transform: uppercase; letter-spacing: 1px;
        display: inline-block; animation: pulseGlow 3s infinite alternate;
        vertical-align: middle; margin-left: 10px;
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(236,72,153,0.3); }
        100% { box-shadow: 0 0 25px rgba(236,72,153,0.7); }
    }

    .action-step {
        display: flex; align-items: center; gap: 16px;
        background: rgba(255,255,255,0.02);
        padding: 16px; border-radius: 16px; margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.04);
        transition: transform 0.3s ease, background 0.3s ease;
        font-size: 1.05rem; font-weight: 400; color: #cbd5e1;
    }
    .action-step:hover {
        transform: translateX(8px); background: rgba(255,255,255,0.06);
        border-color: rgba(255,255,255,0.1);
    }
    .step-number {
        background: linear-gradient(135deg, #10b981, #047857); color: white;
        width: 32px; height: 32px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.95rem; font-weight: 900; flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(16,185,129,0.4);
    }

    /* Titles and Header enhancements */
    h1, h2, h3, h4 { letter-spacing: -0.5px; }
    h1 { font-family: 'Inter', sans-serif; font-size: 3.5rem !important; font-weight: 900 !important; margin-bottom: 0 !important; letter-spacing: -1.5px !important; }
    
    /* Input Elements inside Streamlit */
    [data-testid="stCameraInput"] > div, [data-testid="stFileUploader"] > div {
        border-radius: 20px; overflow: hidden;
        border: 2px dashed rgba(99,102,241,0.5);
        background: rgba(255,255,255,0.02);
        transition: all 0.3s ease;
    }
    [data-testid="stCameraInput"] > div:hover, [data-testid="stFileUploader"] > div:hover {
        border-color: rgba(16,185,129,0.8); background: rgba(16,185,129,0.05);
    }

    /* Progress and Status Tweaks */
    [data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #10b981, #34d399); }

    /* Custom Scrollbar for a polished feel */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #cbd5e1; }
</style>
""", unsafe_allow_html=True)
# (Using DISEASE_INFO and extract_features from utils.py)


# ===============================
# MODEL & SCALER LOADING
# ===============================
@st.cache_resource
def get_cached_model():
    """Load model and scaler once via utils; cache for the app lifetime."""
    try:
        return load_model_and_scaler()
    except FileNotFoundError as e:
        st.error(f"🚨 {e}")
        st.stop()

model, scaler = get_cached_model()

# Detect feature space once at startup
_feature_mode = get_feature_mode(model)


# ===============================
# IMAGE DECODING (stream-safe)
# ===============================
def decode_image_source(source_file, source_type: str = "upload"):
    """
    Reads source file bytes ONCE and caches decoded image in session_state.
    Prevents stream-exhaustion bug on Streamlit re-runs.
    """
    file_key = f"{source_type}_{source_file.name}_{source_file.size}"
    if st.session_state.get("cached_img_key") != file_key:
        raw = source_file.read()
        if not raw:
            return None
        arr = np.asarray(bytearray(raw), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        st.session_state["cached_img"] = img
        st.session_state["cached_img_key"] = file_key
    return st.session_state["cached_img"]


# ===============================
# SESSION HISTORY
# ===============================
def add_to_history(plant: str, disease: str, confidence: float, source: str):
    if "history" not in st.session_state:
        st.session_state["history"] = []
    record = {
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "plant": plant,
        "disease": disease,
        "confidence": round(confidence, 1),
        "source": source,
    }
    st.session_state["history"].insert(0, record)
    st.session_state["history"] = st.session_state["history"][:5]  # Keep last 5


# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("https://img.icons8.com/color/144/leaf.png", width=90)
    st.title("PlantPulse Engine")
    st.caption("Hybrid AI + Quantum Plant Diagnostics")
    st.markdown("---")

    st.markdown("### ⚙️ Configuration")
    confidence_threshold = st.slider("AI Confidence Threshold (%)", 0, 100, 70)
    backend_pref = st.selectbox("Quantum Backend", ["Dynamic (Least Busy)", "Simulator Only"])
    run_quantum_always = st.toggle("Always Run Quantum", value=False,
        help="If OFF, quantum only runs when AI confidence < threshold (faster).")
    camera_master_switch = st.toggle("Live Camera Active", value=True,
        help="Turn OFF to disable camera access and save power/resources.")

    st.markdown("---")
    st.markdown("### 🌡️ Environmental Context")
    env = simulate_environment()
    ec1, ec2 = st.columns(2)
    with ec1:
        st.caption("Temp")
        st.write(f"{env['temp']}°C")
    with ec2:
        st.caption("Humidity")
        st.write(f"{env['humidity']}%")

    st.markdown("---")
    st.markdown("### 📋 Model Info")
    n_classes = len(model.classes_) if hasattr(model, "classes_") else "N/A"
    st.metric("Disease Classes", n_classes)
    st.metric("Features Used", model.n_features_in_)

    if _feature_mode == FEATURE_MODE_RAW:
        st.warning(
            "⚠️ **Legacy Model** — trained with raw pixels (49,152 features). "
            "Run `python main.py` to retrain for much better accuracy."
        )
    else:
        st.success("✅ Enhanced model — histogram features (63 dims)")
        if os.path.exists("plant_scaler.pkl"):
            st.success("✅ Scaler loaded")
        else:
            st.warning("⚠️ No scaler — retrain with `python main.py`")

    if os.path.exists("training_report.txt"):
        with open("training_report.txt") as f:
            report_text = f.read()
        with st.expander("📄 Last Training Report"):
            st.code(report_text, language="text")

    # ── PROJECT STATUS PANEL ──────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔍 Project Status")

    def _status_row(label: str, ok: bool, detail: str = ""):
        icon = "🟢" if ok else "🔴"
        msg  = f"{icon} **{label}**"
        if detail:
            msg += f"  \n&nbsp;&nbsp;&nbsp;`{detail}`"
        st.markdown(msg, unsafe_allow_html=True)

    # 1. Model file
    _status_row("Model file", os.path.exists("plant_model.pkl"),
                "plant_model.pkl found" if os.path.exists("plant_model.pkl") else "Missing — run python main.py")

    # 2. Scaler file
    _status_row("Scaler file", os.path.exists("plant_scaler.pkl"),
                "plant_scaler.pkl found" if os.path.exists("plant_scaler.pkl") else "Missing — retrain for best accuracy")

    # 3. Model loads
    _status_row("Model loads OK", model is not None,
                f"{len(model.classes_)} classes, {model.n_features_in_} features" if model else "Load failed")

    # 4. Feature extraction
    try:
        import numpy as _np
        _dummy = _np.zeros((64, 64, 3), dtype=_np.uint8)
        from utils import extract_for_model as _efm
        _mode = get_feature_mode(model)
        _fv   = _efm(_dummy, model)
        _expected_dim = model.n_features_in_
        _feat_ok = _fv.shape == (1, _expected_dim)
    except Exception as _fe:
        _feat_ok = False
        _expected_dim = "Unknown"
    _status_row("Feature extraction", _feat_ok,
                f"Mode: {_mode} | Dims: {_expected_dim}" if _feat_ok else str(_fe))

    # 5. Predict pipeline (end-to-end with dummy image)
    try:
        _pi = predict_image
        _r = _pi(_dummy, model, scaler)
        _pred_ok = "plant" in _r and "confidence" in _r
    except Exception as _pe:
        _pred_ok = False
    _status_row("Predict pipeline", _pred_ok,
                f"Returns: plant={_r.get('plant','?')}, conf={_r.get('confidence','?')}%" if _pred_ok else str(_pe))

    # 6. Quantum circuit builds
    try:
        _qc, _ent = build_quantum_circuit(_dummy)
        _qc_ok = _qc.num_qubits == 4
    except Exception as _qe:
        _qc_ok = False
    _status_row("Quantum circuit", _qc_ok,
                f"{_qc.num_qubits}-qubit circuit, entropy={_ent:.3f}" if _qc_ok else str(_qe))

    # 7. PlantNet API
    _pnet_token = os.getenv("PLANTNET_API_KEY", "")
    _status_row("PlantNet API", bool(_pnet_token),
                "API Key present" if _pnet_token else "Key missing — set PLANTNET_API_KEY in .env")

    # 8. Crop.Health API
    _crop_token = os.getenv("CROP_HEALTH_API_KEY", "")
    _status_row("Crop.Health API", bool(_crop_token),
                "API Key present" if _crop_token else "Key missing — set CROP_HEALTH_API_KEY in .env")

    # 9. Perenual API
    _per_token = os.getenv("PERENUAL_API_KEY", "")
    _status_row("Perenual Care API", bool(_per_token),
                "API Key present" if _per_token else "Key missing — set PERENUAL_API_KEY in .env")

    # Overall
    _all_ok = all([os.path.exists("plant_model.pkl"), model is not None, _feat_ok, _pred_ok, _qc_ok])
    if _all_ok:
        st.success("✅ All systems operational")
    else:
        st.error("❌ One or more systems need attention (see above)")

    st.markdown("---")
    # Session history in sidebar
    st.markdown("### 🕐 Session History")
    history = st.session_state.get("history", [])
    if history:
        for rec in history:
            badge = "🟢" if rec["disease"].lower() == "healthy" else "🔴"
            st.markdown(
                f"<div class='history-card'>"
                f"{badge} <b>{rec['plant']}</b> — {rec['disease']}<br>"
                f"<span style='color:#64748b'>{rec['confidence']}% · {rec['source']} · {rec['time']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        if st.button("📥 Export History to CSV", use_container_width=True):
            import pandas as pd
            df = pd.DataFrame(history)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="plant_diagnosis_history.csv", mime='text/csv')
    else:
        st.caption("No analyses yet this session.")


# ===============================
# MAIN UI
# ===============================
st.markdown("# 🌿 PlantPulse <span class='quantum-badge'>AI + QUANTUM</span>", unsafe_allow_html=True)
st.write("Upload a leaf image **or snap a live photo** for real-time AI + Quantum analysis.")

col1, col2 = st.columns([1, 1], gap="large")

# ---- INPUT PANEL ----
with col1:
    tab_upload, tab_camera = st.tabs(["📁  Upload Image", "📷  Use Camera"])
    img = None
    input_source = "upload"

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Drop leaf image here...", type=["jpg", "png", "jpeg"],
            label_visibility="collapsed"
        )
        if uploaded_file:
            img = decode_image_source(uploaded_file, "upload")
            input_source = "upload"
            if img is None:
                st.error("❌ Failed to decode image.")
                st.stop()
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
                     caption="📁 Uploaded Specimen", use_container_width=True)

    with tab_camera:
        st.markdown(
            "<p style='color:#94a3b8;font-size:0.85rem;'>📌 Allow camera access, "
            "position leaf in good light, then click <b>Take Photo</b>.</p>",
            unsafe_allow_html=True
        )
        if camera_master_switch:
            camera_file = st.camera_input("Capture leaf", label_visibility="collapsed")
            if camera_file:
                img = decode_image_source(camera_file, "camera")
                input_source = "camera"
                if img is None:
                    st.error("❌ Failed to capture image.")
                    st.stop()
                st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
                         caption="📷 Live Capture", use_container_width=True)
                st.success("✅ Photo captured!")
        else:
            st.warning("🔒 Camera is currently disabled. Turn on 'Live Camera Active' in the sidebar to use this feature.")

# ---- ANALYSIS PANEL ----
with col2:
    active_img = img if img is not None else st.session_state.get("cached_img")

    if active_img is not None:

        # ── HYBRID EXPERT PIPELINE (The New Core) ──────────────────
        st.markdown("### 🧬 Hybrid Diagnostic Pipeline")
        st.caption("PlantNet (Variant) → Crop.Health (Disease) → Qiskit (Risk)")

        run_hybrid = st.button("🚀 RUN FULL EXPERT ANALYSIS", use_container_width=True, type="primary")

        # Track when a new image is loaded vs the report image
        current_img_key = st.session_state.get("cached_img_key", "unknown")
        
        if run_hybrid:
            # 1. PLANTNET (Variant)
            with st.status("🔍 Step 1: Identifying Plant Variant (PlantNet)...") as status:
                p_res = identify_plant_plantnet(active_img)
                if "error" in p_res:
                    st.error(f"⚠️ PlantNet Error: {p_res['error']}")
                    variant, v_score = "Unknown", 0
                else:
                    variant = p_res['plant']
                    v_score = p_res['score']
                    st.write(f"✅ Detected Variant: **{variant}**")
                status.update(label=f"Step 1 Complete: {variant}", state="complete")

            # 2. CROP.HEALTH (Disease/Pathogen)
            with st.status("🩺 Step 2: Pathogen Status (Crop.Health)...") as status:
                c_res = identify_crop_health(active_img)
                if "error" in c_res:
                    st.error(f"⚠️ Crop.Health Error: {c_res['error']}")
                    disease_name, d_conf = "Unknown", 0
                    treatment = "No data available. Check API key status or image quality."
                else:
                    disease_name = c_res['disease']
                    d_conf = c_res['confidence']
                    treatment = c_res['treatment']
                    st.write(f"✅ Pathogen Status: **{disease_name}**")
                status.update(label=f"Step 2 Complete: {disease_name}", state="complete")

            # 3. QUANTUM (Risk Level)
            with st.status("⚛️ Step 3: Quantum Stability Analysis (Qiskit)...") as status:
                qc, entropy = build_quantum_circuit(active_img)
                counts, backend_name = run_quantum(qc, backend_pref)
                risk_score, risk_level = calculate_quantum_risk(counts, entropy)
                leaf_health = 100 - risk_score
                st.write(f"✅ Quantum Result: **{risk_level} Risk**")
                status.update(label="Step 3 Complete", state="complete")

            # 4. PERENUAL (Care Guide)
            with st.status("🌿 Step 4: Maintenance & Care (Perenual)...") as status:
                care_res = get_perenual_care_info(variant)
                if "error" in care_res:
                    st.warning(f"Perenual: {care_res['error']}")
                    care_data = None
                else:
                    care_data = care_res
                    st.write("✅ Care Guide Loaded")
                status.update(label="Step 4 Complete", state="complete")

            # SAVE TO SESSION STATE
            st.session_state["expert_report"] = {
                "img_key": current_img_key,
                "variant": variant, "v_score": v_score,
                "disease_name": disease_name, "d_conf": d_conf, "treatment": treatment,
                "risk_score": risk_score, "risk_level": risk_level, "leaf_health": leaf_health,
                "care_data": care_data
            }
            add_to_history(variant, disease_name, d_conf, "expert_pipeline")
            st.balloons()

        # If we have a report in memory and the image hasn't changed, render it
        report = st.session_state.get("expert_report")
        if report and report["img_key"] == current_img_key:
            variant, disease_name = report["variant"], report["disease_name"]
            d_conf, care_data = report["d_conf"], report["care_data"]
            leaf_health, risk_score = report["leaf_health"], report["risk_score"]
            risk_level, treatment = report["risk_level"], report["treatment"]

            # --- DISPLAY INTEGRATED EXPERT REPORT ---
            st.markdown("---")
            st.markdown("## 📋 Integrated Health Report")
            
            # Health Score Gauge (Simulated with progress bar)
            h_color = "#10b981" if leaf_health > 70 else "#f59e0b" if leaf_health > 40 else "#ef4444"
            st.markdown(f"### Overall Leaf Health: <span style='color:{h_color}'>{leaf_health}%</span>", unsafe_allow_html=True)
            st.progress(leaf_health / 100)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<div class='metric-card'><h4>Target Variant</h4><h2>{variant}</h2></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='metric-card'><h4>Pathogen Status</h4><h2>{disease_name}</h2></div>", unsafe_allow_html=True)
            with c3:
                risk_color = "#ef4444" if risk_level == "CRITICAL" else "#f59e0b" if risk_level == "MODERATE" else "#10b981"
                st.markdown(f"<div class='metric-card'><h4>Risk Level</h4><h2 style='color:{risk_color};'>{risk_level}</h2></div>", unsafe_allow_html=True)
            
            # Re-defining the columns better for alignment
            st.markdown("---")
            col_info1, col_info2 = st.columns([1, 1], gap="medium")
            
            with col_info1:
                st.markdown("#### 🏥 Remedial Action Plan")
                if "healthy" in disease_name.lower():
                    st.success("✅ **HEALTHY SPECIMEN**\n\nNo active pathogens detected. The structural integrity of the leaf is within normal parameters.")
                    st.markdown("""
                    <div class='action-step'><div class='step-number'>1</div>Maintain normal watering Schedule.</div>
                    <div class='action-step'><div class='step-number'>2</div>Ensure adequate sunlight (4-6 hours).</div>
                    <div class='action-step'><div class='step-number'>3</div>Monitor for seasonal pests.</div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"⚠️ **PATHOGEN DETECTED: {disease_name.upper()}**")
                    st.warning(f"**Field Treatment:**\n\n{treatment}")
                    
                    local_info = get_disease_info(disease_name)
                    if local_info["tips"] != FALLBACK_INFO["tips"]:
                        st.info(f"💡 **AI Expert Suggestion:** {local_info['tips']}")

                    st.markdown("##### 🛒 Recommended Solutions & Pesticides")
                    purchase_links = get_remedy_purchase_links(disease_name)
                    for link in purchase_links:
                        st.markdown(
                            f"<a href='{link['url']}' target='_blank' class='purchase-button'>"
                            f"{link['icon']} Buy {disease_name} Remedy on {link['store']}"
                            f"</a>", 
                            unsafe_allow_html=True
                        )

            with col_info2:
                st.markdown("#### 🌿 Species & Care Intelligence")
                if care_data:
                    watering = str(care_data.get('watering', 'N/A')).title()
                    sunlight = str(care_data.get('sunlight', 'N/A'))
                    cycle = str(care_data.get('cycle', 'N/A')).title()
                    care_level = str(care_data.get('care_level', 'N/A')).upper()
                    
                    st.write(f"**Watering Needs:** {watering} 💧")
                    st.write(f"**Sunlight Exposure:** {sunlight} ☀️")
                    st.write(f"**Growth Cycle:** {cycle} 🔄")
                    st.write(f"**Maintenance Level:** {care_level} 🛠️")
                    with st.expander("📖 Botanical Description"):
                        st.write(str(care_data.get('description', 'No description available')))
                else:
                    st.info("No botanical data found for this specific variant.")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### ⚛️ Stability Analysis (Quantum)")
                st.caption("Determined via 4-qubit probability entanglement state.")
                q_col1, q_col2 = st.columns(2)
                with q_col1:
                    st.metric("Risk Score", f"{risk_score}%")
                with q_col2:
                    st.metric("Quantum Stability", f"{100 - risk_score}%")

            # Move Actions and PDF Download to a balanced full-width section
            st.markdown("---")
            action_c1, action_c2 = st.columns([1, 1], gap="medium")
            
            with action_c1:
                # Expert Chat Invite
                st.markdown("#### 💬 Talk to Virtual Pathologist")
                with st.expander("Ask Dr. Leaf"):
                    st.write("Our AI-driven pathologist 'Dr. Leaf' is available for deep-dive questions.")
                    
                    # We initialize Dr Leaf logic robustly to handle re-runs
                    if "dr_leaf_chat" not in st.session_state:
                        st.session_state["dr_leaf_chat"] = []
                        
                    for msg in st.session_state["dr_leaf_chat"]:
                        st.info(msg)
                        
                    user_q = st.text_input("Ask a question about this diagnosis:")
                    if user_q:
                        reply = f"Dr. Leaf says: For {disease_name}, ensure you rotate crops and check for {variant} core stability weekly. You asked: '{user_q}'?"
                        st.session_state["dr_leaf_chat"].append(reply)
                        st.rerun()
            
            with action_c2:
                st.markdown("#### 📥 Document Export")
                # PDF Download Feature
                pdf_bytes = generate_pdf_report(variant, disease_name, d_conf, risk_level, treatment)
                st.download_button(
                    label="📄 Download Professional Diagnostic Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"PlantPulse_Report_{variant}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            add_to_history(variant, disease_name, d_conf, "expert_pipeline")
            st.balloons()

        st.markdown("---")
        with st.expander("🔬 Legacy Classical AI Analysis (Local Model)"):
            # (Keep the existing classical logic here for reference)
            with st.spinner("Processing local AI..."):
                try:
                    result = predict_image(active_img, model, scaler)
                    st.write(f"Local AI thinks: **{result['plant']}** with **{result['disease']}**")
                    st.progress(result['confidence']/100, text=f"Local Confidence: {result['confidence']}%")
                except Exception as e:
                    st.error(f"Local AI Error: {e}")

        # (Remove the old individual expanders for PlantNet and Crop.Health as they are now in the main pipeline)

        # ── 3. SAVE TO HISTORY & DOWNLOAD (Placeholder logic removed, handled inside pipeline blocks)
        st.info("💡 Run the **Hybrid Diagnostic Pipeline** above for full expert analysis and downloadable reports.")

    else:
        # Clear stale cache when no image present
        for k in ["cached_img", "cached_img_key"]:
            st.session_state.pop(k, None)

        st.markdown("""
        <div style='text-align:center;padding:80px 20px;color:#64748b;'>
            <img src='https://img.icons8.com/dotty/80/64748b/camera.png'/>
            <br><br>
            <span style='font-size:1.1rem;'>
                Use the <b>Upload</b> or <b>Camera</b> tab on the left<br>
                to provide a leaf specimen for analysis.
            </span>
        </div>
        """, unsafe_allow_html=True)
