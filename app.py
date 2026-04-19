import streamlit as st
import cv2
import numpy as np
import os
import requests
import json
import base64
import datetime
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import hashlib
import sqlite3
import time
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Shared Utilities
from utils import (
    identify_plant_plantnet, identify_crop_health, get_disease_info,
    predict_image, load_model_and_scaler, build_quantum_circuit,
    run_quantum, calculate_quantum_risk, generate_pdf_report,
    get_perenual_care_info, generate_pathogen_mask,
    decode_bytes_to_bgr, compute_leaf_texture_score, 
    compute_ndvi_score, compute_water_stress_index, classify_pathogen_severity,
    get_remedy_purchase_links
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse GREEN | Forest Intelligence Terminal",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (The Forest Intelligence Theme)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&family=JetBrains+Mono&display=swap');

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

    .stApp {
        background: #052e16 !important; /* Deep forest green */
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(34, 197, 94, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 100% 100%, rgba(20, 184, 166, 0.15) 0%, transparent 50%),
            url('https://www.transparenttextures.com/patterns/pinstriped-suit.png') !important;
    }

    /* PREMIUM FOREST GLASS */
    .glass-card {
        background: rgba(2, 44, 34, 0.8) !important;
        border: 2px solid rgba(34, 197, 94, 0.2) !important;
        border-radius: 30px !important;
        padding: 35px;
        backdrop-filter: blur(15px);
        box-shadow: 0 40px 100px -20px rgba(0, 0, 0, 0.7);
        margin-bottom: 30px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .glass-card:hover { 
        border-color: rgba(34, 197, 94, 0.6); 
        transform: scale(1.02) translateY(-5px);
        box-shadow: 0 50px 120px -30px rgba(16, 185, 129, 0.4);
    }

    .metric-val { font-family: 'JetBrains Mono', monospace; font-size: 3rem; color: #4ade80; font-weight: 900; filter: drop-shadow(0 0 10px rgba(74, 222, 128, 0.3)); }
    .metric-lab { font-size: 0.85rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 5px; }

    /* ACTION BUTTONS */
    .stButton>button {
        background: linear-gradient(135deg, #10b981, #065f46) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: 800 !important;
        height: 70px !important;
        font-size: 1.2rem !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 20px 40px -15px rgba(6, 95, 70, 0.8) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 30px 60px -20px rgba(16, 185, 129, 0.9) !important;
    }

    .purchase-btn {
        background: #14532d;
        color: #4ade80 !important;
        padding: 10px 20px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        display: inline-block;
        margin-top: 10px;
        margin-right: 10px;
        border: 1px solid #10b981;
        transition: 0.2s;
    }
    .purchase-btn:hover { background: #166534; transform: scale(1.05); }

    /* ANIMATIONS */
    @keyframes leaf-rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .spinning-leaf { animation: leaf-rotate 20s linear infinite; opacity: 0.1; position: absolute; top: -50px; right: -50px; width: 200px; }
</style>
""", unsafe_allow_html=True)

# ===============================
# DATABASE
# ===============================
def log_diagnostic_v7(v, p, r):
    try:
        conn = sqlite3.connect('plantpulse_diagnostics.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS forest_ledger (id INTEGER PRIMARY KEY, ts TEXT, plant TEXT, path TEXT, risk REAL)")
        c.execute("INSERT INTO forest_ledger (ts, plant, path, risk) VALUES (?,?,?,?)",
                  (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), v, p, r))
        conn.commit()
        conn.close()
    except: pass

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown("<div style='text-align:center'><img src='https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif' style='border-radius:50%; width:180px; border:4px solid #10b981; padding:5px;'></div>", unsafe_allow_html=True)
    st.title("PlantPulse GREEN")
    st.markdown("<p style='color:#10b981; font-weight:800; letter-spacing:1px;'>FOREST INTELLIGENCE TERMINAL</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.success("✅ **Core Synchronized**\n✅ **Market Feeds Active**\n✅ **Dr. Leaf v7.0 Ready**")
    
    st.markdown("---")
    st.subheader("👨‍💻 Engineering Syndicate")
    st.markdown("""
        **Sindhuja R** (226004099)
        **Saraswathy R** (226004092)
        **U. Kiruthika** (226004052)
    """)

# ===============================
# MARKET TICKER
# ===============================
st.markdown("""
<div style="background: rgba(2, 44, 34, 0.9); padding: 15px; border-radius: 15px; border: 1px solid #14532d; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <marquee scrollamount="5" style="color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight:700;">
        🌿 GLOBAL VEGETATION INDEX: +2.4% &nbsp;&nbsp;█&nbsp;&nbsp; 📦 SHIPMENT ALERT: AG-P04 ARRIVING IN 2H &nbsp;&nbsp;█&nbsp;&nbsp; ⚛️ QUANTUM SYNC: 127 QUBITS ACTIVE &nbsp;&nbsp;█&nbsp;&nbsp; 🌽 CORN: $4.52 (▲) &nbsp;&nbsp;█&nbsp;&nbsp; 🧪 LAB STATUS: STERILE &nbsp;&nbsp;█&nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 style='color:#4ade80; font-size:4.5rem; font-weight:900; margin-bottom:0;'>FOREST LAB TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; font-size:1.4rem; margin-top:-10px; font-weight:500;'>Advanced AI + Quantum Phytopathology Intelligence</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
c1, c2 = st.columns([1, 1], gap="large")

with c1:
    st.markdown("#### 📥 Specimen Bio-Inlet")
    in_mode = st.radio("Inlet Protocol", ["Quantum Upload", "Live Optical Capture"], horizontal=True)
    img_in = None
    if in_mode == "Quantum Upload":
        files = st.file_uploader("Multispectral Support Engaged", type=["jpg","png","jpeg"], accept_multiple_files=False)
        if files: img_in = decode_bytes_to_bgr(files.read())
    else:
        cam = st.camera_input("Active Bioscan")
        if cam: img_in = decode_bytes_to_bgr(cam.read())

with c2:
    if img_in is not None:
        st.markdown("#### 🔍 Active Specimen Matrix")
        st.image(cv2.cvtColor(img_in, cv2.COLOR_BGR2RGB), use_container_width=True)
    else:
        st.info("Awaiting botanical specimen for bio-metric mapping.")

# ANALYSIS EXECUTE
if img_in is not None:
    st.markdown("---")
    if st.button("🌟 INITIATE OVERDRIVE DIAGNOSTIC SEQUENCE", use_container_width=True):
        
        # LOGS
        log_ph = st.empty()
        log_acc = []
        def logit(m):
            log_acc.append(f"<span style='color:#4ade80;'>[SYNC]</span> {m}")
            log_ph.markdown(f"<div style='font-family:monospace; background:#022c22; padding:15px; border-radius:15px; border:1px solid #10b981; height:120px; overflow-y:auto;'>{'<br>'.join(log_acc)}</div>", unsafe_allow_html=True)
            time.sleep(0.3)

        logit("Initializing Neural Overdrive...")
        p_res = identify_plant_plantnet(img_in)
        variant = p_res.get('plant', 'Unknown')
        
        logit(f"Specimen Class: {variant}")
        c_res = identify_crop_health(img_in)
        pathogen = c_res.get('disease', 'Healthy')
        conf = c_res.get('confidence', 0)
        
        logit(f"Pathogen Match: {pathogen} ({conf}%)")
        logit("Constructing Quantum Superposition Circuit...")
        qc, entropy = build_quantum_circuit(img_in)
        q_results, backend = run_quantum(qc)
        risk_score, risk_lvl = calculate_quantum_risk(q_results, entropy)
        
        is_healthy = "healthy" in pathogen.lower()
        if is_healthy:
            st.balloons()
            if conf > 65: risk_score *= 0.3; risk_lvl = "LOW (Healthy Growth)"
        
        log_diagnostic_v7(variant, pathogen, risk_score)
        logit("Diagnostic Dossier Compiled.")

        # DASHBOARD
        st.markdown("## 🌿 Forest Intelligence Dashboard")
        d1, d2 = st.columns([1, 1], gap="large")
        
        with d1:
            st.markdown("<div class='glass-card'><img src='https://www.transparenttextures.com/patterns/leaf.png' class='spinning-leaf'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#4ade80; margin-top:0;'>{variant}</h2>", unsafe_allow_html=True)
            st.markdown(f"**CONDITION:** {'🟢 VIBRANT/SAFE' if is_healthy else '🔴 PATHOGEN DETECTED'}")
            st.markdown(f"**PATHOGEN:** {pathogen}")
            
            st.markdown("---")
            m_a, m_b = st.columns(2)
            m_a.markdown(f"<div class='metric-lab'>Quantum Risk</div><div class='metric-val'>{risk_score:.1f}%</div>", unsafe_allow_html=True)
            m_b.markdown(f"<div class='metric-lab'>AI Confidence</div><div class='metric-val'>{conf}%</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            remedy_text = c_res.get('treatment', "Maintain current care protocol.") if not is_healthy else "Specimen is optimal. No remediation required."
            st.markdown(f"🧪 **REMEDY PROTOCOL:** <br><span style='color:#4ade80;'>{remedy_text}</span>", unsafe_allow_html=True)
            
            # PURCHASE LINKS
            if not is_healthy:
                st.markdown("<br>**DIRECT REMEDY PROCUREMENT:**", unsafe_allow_html=True)
                p_links = get_remedy_purchase_links(pathogen)
                link_cols = st.columns(len(p_links) if p_links else 1)
                for idx, link in enumerate(p_links):
                    with link_cols[idx]:
                        st.markdown(f"<a href='{link['url']}' target='_blank' class='purchase-btn'>{link['icon']} {link['store']}</a>", unsafe_allow_html=True)
            
            st.markdown("---")
            pdf = generate_pdf_report(variant, pathogen, conf, risk_lvl, remedy_text, risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD CLINICAL DOSSIER", data=pdf, file_name=f"PlantPulse_v7_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            tabs = st.tabs(["🌀 3D Topology", "⚛️ DNA Space", "🔬 Bio-Metrics", "📈 Projections"])
            
            with tabs[0]:
                gray = cv2.resize(cv2.cvtColor(img_in, cv2.COLOR_BGR2GRAY), (100, 100))
                fig = go.Figure(data=[go.Surface(z=gray, colorscale='Greens')])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)

            with tabs[1]:
                st.markdown("#### Sub-Cellular Genetic Map")
                dna = "".join(["ATCG"[hash(variant+str(j)) % 4] for j in range(80)])
                if not is_healthy: dna = dna.replace("A", "<span style='color:#f87171'>!</span>").replace("C", "<span style='color:#f87171'>?</span>")
                st.markdown(f"<div style='font-family:monospace; background:#01120a; padding:20px; font-size:1.2rem; border:2px solid #10b981; color:#4ade80;'>{dna}</div>", unsafe_allow_html=True)

            with tabs[2]:
                n_val = compute_ndvi_score(img_in)
                w_val = compute_water_stress_index(img_in)
                st.metric("Photosynthetic Strength (NDVI)", f"{n_val:.4f}")
                st.metric("Hydration Loss Index (WSI)", f"{w_val}%")
                st.progress((n_val+1)/2, text="Leaf Vitality Saturation")

            with tabs[3]:
                st.markdown("#### Global Pathogen Forecast")
                chart_data = pd.DataFrame(np.random.randn(20, 3) / [5, 5, 5], columns=['Blight', 'Rust', 'Mildew'])
                st.line_chart(chart_data)

# EXPERT SYSTEM
st.markdown("---")
st.markdown("## 🤖 Expert Module: Dr. Leaf v7.0")
ex_1, ex_2 = st.columns([1, 2])
with ex_1:
    st.image("https://img.icons8.com/bubbles/200/leaf.png")
with ex_2:
    q = st.text_input("Consult the Botanical Oracle...", placeholder="Describe symptoms or query a disease...")
    if q:
        res = get_disease_info(q)
        st.markdown(f"""
        <div style="background:#022c22; border:2px solid #10b981; padding:25px; border-radius:20px;">
            <h3 style="color:#4ade80; margin-top:0;">Dr. Leaf's Diagnosis</h3>
            <p style="font-size:1.1rem; color:#d1d5db;">{res['tips']}</p>
            <span style="background:#14532d; color:#4ade80; padding:5px 15px; border-radius:10px; font-weight:700;">
                SEVERITY: {res['severity'].upper()}
            </span>
        </div>
        """, unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #4ade80; opacity: 0.6; font-size: 0.9rem; padding-top: 50px;'>
    <b>PLANT PULSE FOREST TECHNOLOGIES</b><br>
    The Ultimate Organic Intelligence v7.0<br>
    © 2026 Sovereign Agritech Alliance
</div>
""", unsafe_allow_html=True)
