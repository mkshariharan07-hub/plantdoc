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

# Force UTF-8 encoding for standard output to avoid Windows console errors with emojis
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Shared utilities — single source of truth for features & prediction
from utils import (
    predict_image, 
    get_disease_info,
    get_feature_mode, 
    load_model_and_scaler,
    decode_bytes_to_bgr, 
    build_quantum_circuit,
    run_quantum,
    extract_features,
    FEATURE_DIM,
    identify_plant_plantnet,
    identify_crop_health,
    calculate_quantum_risk,
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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

    .main { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; }

    .stButton>button {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: white; border: none; border-radius: 12px;
        padding: 0.6rem 1.2rem; font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16,185,129,0.3);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16,185,129,0.4); }

    .metric-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px; padding: 1.5rem;
        text-align: center; transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: scale(1.02); border-color: #10b981; }

    .quantum-badge {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white; padding: 4px 12px; border-radius: 50px;
        font-size: 0.8rem; font-weight: 600;
    }

    .severity-high   { background:#ef4444; color:white; padding:4px 12px; border-radius:50px; font-weight:600; font-size:0.85rem; }
    .severity-medium { background:#f59e0b; color:white; padding:4px 12px; border-radius:50px; font-weight:600; font-size:0.85rem; }
    .severity-low    { background:#10b981; color:white; padding:4px 12px; border-radius:50px; font-weight:600; font-size:0.85rem; }

    .history-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px; padding: 0.8rem 1rem;
        margin-bottom: 8px; font-size: 0.85rem;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px; background: rgba(255,255,255,0.04);
        border-radius: 14px; padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px; padding: 8px 20px;
        font-weight: 600; color: #94a3b8; background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #10b981, #059669) !important;
        color: white !important;
    }
    [data-testid="stCameraInput"] > div {
        border-radius: 16px; overflow: hidden;
        border: 2px solid rgba(99,102,241,0.4);
        box-shadow: 0 0 20px rgba(99,102,241,0.15);
    }
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
                     caption="📁 Uploaded Specimen", use_column_width=True)

    with tab_camera:
        st.markdown(
            "<p style='color:#94a3b8;font-size:0.85rem;'>📌 Allow camera access, "
            "position leaf in good light, then click <b>Take Photo</b>.</p>",
            unsafe_allow_html=True
        )
        camera_file = st.camera_input("Capture leaf", label_visibility="collapsed")
        if camera_file:
            img = decode_image_source(camera_file, "camera")
            input_source = "camera"
            if img is None:
                st.error("❌ Failed to capture image.")
                st.stop()
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
                     caption="📷 Live Capture", use_column_width=True)
            st.success("✅ Photo captured!")

# ---- ANALYSIS PANEL ----
with col2:
    active_img = img if img is not None else st.session_state.get("cached_img")

    if active_img is not None:

        # ── HYBRID EXPERT PIPELINE (The New Core) ──────────────────
        st.markdown("### 🧬 Hybrid Diagnostic Pipeline")
        st.caption("PlantNet (Variant) → Crop.Health (Disease) → Qiskit (Risk)")

        run_hybrid = st.button("🚀 RUN FULL HYBRID ANALYSIS", use_container_width=True, type="primary")

        if run_hybrid:
            # 1. PLANTNET (Variant)
            with st.status("🔍 Step 1: Identifying Plant Variant (PlantNet)...") as status:
                p_res = identify_plant_plantnet(active_img)
                if "error" in p_res:
                    st.error(f"PlantNet: {p_res['error']}")
                    variant, v_score = "Unknown", 0
                else:
                    variant = p_res['plant']
                    v_score = p_res['score']
                    st.write(f"✅ Detected Variant: **{variant}** ({v_score}%)")
                status.update(label="Step 1 Complete", state="complete")

            # 2. CROP.HEALTH (Disease)
            with st.status("🩺 Step 2: Pathogen Detection (Crop.Health)...") as status:
                c_res = identify_crop_health(active_img)
                if "error" in c_res:
                    st.error(f"Crop.Health: {c_res['error']}")
                    disease_name, d_conf = "Unknown", 0
                    treatment = "No data available."
                else:
                    disease_name = c_res['disease']
                    d_conf = c_res['confidence']
                    treatment = c_res['treatment']
                    st.write(f"✅ Detected Disease: **{disease_name}** ({d_conf}%)")
                status.update(label="Step 2 Complete", state="complete")

            # 3. QUANTUM (Risk Level)
            with st.status("⚛️ Step 3: Quantum Risk Analysis (Qiskit)...") as status:
                qc, entropy = build_quantum_circuit(active_img)
                counts, backend_name = run_quantum(qc, backend_pref)
                risk_score, risk_level = calculate_quantum_risk(counts, entropy)
                st.write(f"✅ Quantum Result: **{risk_level}** (Risk Score: {risk_score})")
                status.update(label="Step 3 Complete", state="complete")

            # --- DISPLAY INTEGRATED RESULTS ---
            st.markdown("---")
            st.markdown(f"#### 🏁 Final Diagnostic Report")
            
            r1, r2, r3 = st.columns(3)
            with r1:
                st.markdown(f"<div class='metric-card'><h4>Variant</h4><h2>{variant}</h2></div>", unsafe_allow_html=True)
            with r2:
                st.markdown(f"<div class='metric-card'><h4>Pathogen</h4><h2>{disease_name}</h2></div>", unsafe_allow_html=True)
            with r3:
                risk_color = "#ef4444" if risk_level == "CRITICAL" else "#f59e0b" if risk_level == "MODERATE" else "#10b981"
                st.markdown(f"<div class='metric-card'><h4>Risk Level</h4><h2 style='color:{risk_color};'>{risk_level}</h2></div>", unsafe_allow_html=True)

            # Remedial Actions
            st.markdown("### 💊 Remedial Actions")
            if "healthy" in disease_name.lower():
                st.success("Plant appears healthy. No immediate treatment needed. Continue standard care.")
            else:
                st.warning(f"**Targeted Treatment for {disease_name}:**")
                st.write(treatment)
                
                # Check local knowledge base for additional tips
                local_info = get_disease_info(disease_name)
                if local_info["tips"] != _FALLBACK_INFO["tips"]:
                    st.info(f"💡 **Additional AI Guidance:** {local_info['tips']}")

            # Save to history
            add_to_history(variant, disease_name, d_conf, "hybrid_pipeline")
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
        </div>
        """, unsafe_allow_html=True)

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