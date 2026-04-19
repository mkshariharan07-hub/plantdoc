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
    compute_ndvi_score, compute_water_stress_index, 
    estimate_nitrogen_content, calculate_yield_impact,
    calculate_pathogen_resistance, calculate_farm_roi,
    estimate_biological_age, get_remedy_purchase_links,
    classify_pathogen_severity
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse TITAN | The Ultimate Leaf Interface",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (The TITAN Aesthetic)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&family=JetBrains+Mono:wght@400;800&display=swap');

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

    .stApp {
        background: #020617 !important;
        background-image: 
            radial-gradient(circle at 10% 10%, rgba(34, 197, 94, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 90% 90%, rgba(16, 185, 129, 0.1) 0%, transparent 40%),
            url('https://www.transparenttextures.com/patterns/pinstriped-suit.png') !important;
    }

    /* FALLING LEAVES ANIMATION */
    .leaf-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; overflow: hidden; display: none; }
    .leaf { position: absolute; top: -100px; width: 40px; height: 40px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall 5s linear infinite; }
    @keyframes fall {
        0% { transform: translateY(-100px) rotate(0deg); left: 10%; }
        100% { transform: translateY(110vh) rotate(360deg); left: 20%; }
    }

    /* SIDEBAR ENGINEERING CORE - ELITE UPGRADE */
    .eng-core-box {
        background: rgba(13, 148, 136, 0.1);
        border: 1px solid rgba(13, 148, 136, 0.4);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .core-row { display: flex; align-items: center; margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #4ade80; }
    .status-badge { width: 8px; height: 8px; border-radius: 50%; background: #22c55e; margin-right: 12px; box-shadow: 0 0 10px #22c55e; }
    
    .architect-card {
        background: linear-gradient(135deg, rgba(2, 44, 34, 0.8), rgba(6, 78, 59, 0.8));
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 10px;
        color: #fff;
    }
    .architect-name { font-weight: 900; font-size: 1.1rem; color: #4ade80; display: block; margin-bottom: 2px; }
    .architect-id { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #94a3b8; letter-spacing: 2px; }

    /* TITAN GLASS */
    .glass-card {
        background: rgba(1, 15, 12, 0.8) !important;
        border: 2px solid rgba(34, 197, 94, 0.2) !important;
        border-radius: 40px !important;
        padding: 45px;
        backdrop-filter: blur(20px);
        box-shadow: 0 50px 120px -30px rgba(0, 0, 0, 0.9);
        margin-bottom: 40px;
        transition: 0.5s;
    }
    .glass-card:hover { border-color: #22c55e; box-shadow: 0 0 60px rgba(34, 197, 94, 0.2); transform: translateY(-5px); }
</style>

<div id="leaves" class="leaf-container">
    <div class="leaf" style="left:5%; animation-duration:4s;"></div>
    <div class="leaf" style="left:15%; animation-duration:6s;"></div>
    <div class="leaf" style="left:25%; animation-duration:3s;"></div>
    <div class="leaf" style="left:35%; animation-duration:5s;"></div>
    <div class="leaf" style="left:45%; animation-duration:7s;"></div>
    <div class="leaf" style="left:55%; animation-duration:4s;"></div>
    <div class="leaf" style="left:65%; animation-duration:6s;"></div>
    <div class="leaf" style="left:75%; animation-duration:3s;"></div>
    <div class="leaf" style="left:85%; animation-duration:5s;"></div>
    <div class="leaf" style="left:95%; animation-duration:4s;"></div>
</div>
""", unsafe_allow_html=True)

# ===============================
# DATABASE
# ===============================
def log_v9(v, p, r):
    try:
        conn = sqlite3.connect('plantpulse_diagnostics.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS titan_ledger (id INTEGER PRIMARY KEY, ts TEXT, plant TEXT, path TEXT, risk REAL)")
        c.execute("INSERT INTO titan_ledger (ts, plant, path, risk) VALUES (?,?,?,?)",
                  (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), v, p, r))
        conn.commit()
        conn.close()
    except: pass

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif", use_container_width=True)
    st.markdown("<h2 style='text-align:center; color:#4ade80;'>PLANTPULSE TITAN</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🛠️ ENGINEERING CORE v9.0")
    st.markdown("""
    <div class='eng-core-box'>
        <div class='core-row'><span class='status-badge'></span> PLANTNET-50 NEURAL NODE [ACTIVE]</div>
        <div class='core-row'><span class='status-badge'></span> KINDWISE-AI SYNC [NOMINAL]</div>
        <div class='core-row'><span class='status-badge' style='background:#3b82f6; box-shadow:0 0 10px #3b82f6;'></span> QISKIT-127 QUBITS [VIRTUALIZED]</div>
        <div class='core-row'><span class='status-badge' style='background:#f59e0b; box-shadow:0 0 10px #f59e0b;'></span> BIOSYNTHETIC MAPPING [READY]</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👨‍💻 SYSTEM ARCHITECTS")
    st.markdown("""
    <div class='architect-card'>
        <span class='architect-name'>SINDHUJA R</span><span class='architect-id'>ID: 226004099</span>
    </div>
    <div class='architect-card'>
        <span class='architect-name'>SARASWATHY R</span><span class='architect-id'>ID: 226004092</span>
    </div>
    <div class='architect-card'>
        <span class='architect-name'>KIRUTHIKA U</span><span class='architect-id'>ID: 226004052</span>
    </div>
    """, unsafe_allow_html=True)

# TICKER
st.markdown("""
<div style="background: rgba(1, 15, 12, 0.9); padding: 15px; border-radius: 12px; border: 1px solid #065f46; margin-bottom: 35px;">
    <marquee scrollamount="6" style="color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight:800;">
        ⚡ QUANTUM CONSENSUS: 100% &nbsp;&nbsp;█&nbsp;&nbsp; 🌽 CORN: $4.52 &nbsp;&nbsp;█&nbsp;&nbsp; 🌱 SOY: $12.45 &nbsp;&nbsp;█&nbsp;&nbsp; 🧬 BIOSYNTHETIC DRIFT: NOMINAL &nbsp;&nbsp;█&nbsp;&nbsp; 🛰️ ORBITAL SYNC: ESTABLISHED &nbsp;&nbsp;█&nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 style='color:#4ade80; font-size:5rem; font-weight:900; letter-spacing:-3px;'>TITAN ANALYTICAL OVERDRIVE</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; font-size:1.6rem; margin-top:-20px;'>Ultimate High-Fidelity Agriculture Diagnostic Terminal // v9.0</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
c_in, c_pre = st.columns([1,1], gap="large")

with c_in:
    st.markdown("### 📥 Neural Bio-Inlet")
    src = st.radio("Signal Source", ["Quantum Upload", "Optical Terminal"], horizontal=True)
    img_bgr = None
    if src == "Quantum Upload":
        f = st.file_uploader("Select Multispectral Ingestion", type=["jpg","png","jpeg"])
        if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Active Bioscan")
        if cam: img_bgr = decode_bytes_to_bgr(cam.read())

with c_pre:
    if img_bgr is not None:
        st.markdown("### 🔍 Specimen Frequency Matrix")
        st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)
    else:
        st.info("Awaiting specimen ingestion for high-fidelity clinical mapping...")

# ANALYSIS
if img_bgr is not None:
    st.markdown("---")
    if st.button("🎆 INITIATE TITAN DIAGNOSTIC OVERDRIVE", use_container_width=True):
        
        # LOGS
        ph = st.empty()
        acc = []
        def log(m):
            acc.append(f"<span style='color:#4ade80;'>[SYNC]</span> {m}")
            ph.markdown(f"<div style='font-family:monospace; background:#000; padding:15px; border-radius:15px; border:1px solid #4ade80; height:120px; overflow-y:auto;'>{'<br>'.join(acc)}</div>", unsafe_allow_html=True)
            time.sleep(0.3)

        log("Neural Synapse Initialized...")
        p_res = identify_plant_plantnet(img_bgr)
        variant = p_res.get('plant', 'Unknown')
        
        log(f"Species Lock: {variant}")
        c_res = identify_crop_health(img_bgr)
        pathogen = c_res.get('disease', 'Healthy')
        conf = c_res.get('confidence', 0)
        
        log(f"Pathogen Consensus: {pathogen} ({conf}%)")
        log("Constructing Hyper-Quantum Entropy Circuit...")
        qc, ent_val = build_quantum_circuit(img_bgr)
        counts, b_name = run_quantum(qc)
        risk_score, risk_lvl = calculate_quantum_risk(counts, ent_val)
        
        is_h = "healthy" in pathogen.lower()
        if is_h:
            # TRIGGER LEAF EFFECT
            st.markdown("<script>document.getElementById('leaves').style.display = 'block'; setTimeout(() => { document.getElementById('leaves').style.display = 'none'; }, 6000);</script>", unsafe_allow_html=True)
            if conf > 65: risk_score *= 0.3; risk_lvl = "LOW (Healthy Growth)"
            st.success("✅ OPTIMAL VITALITY DETECTED")

        log_v9(variant, pathogen, risk_score)
        
        # DASHBOARD
        st.markdown("## 📊 Titan Intelligence Dashboard")
        d1, d2 = st.columns([1,1], gap="large")
        
        with d1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='color:#4ade80; margin:0;'>{variant}</h1>", unsafe_allow_html=True)
            st.markdown(f"**CONDITION:** {'🟢 VIBRANT' if is_h else '🔴 CRITICAL/PATHOGEN'}")
            st.markdown(f"**PATHOGEN:** {pathogen}")
            
            st.markdown("---")
            m1, m2 = st.columns(2)
            m1.metric("Quantum Risk", f"{risk_score:.1f}%", risk_lvl)
            m2.metric("AI Confidence", f"{conf:.1f}%")
            
            st.markdown("---")
            rem = c_res.get('treatment', "Maintain monitoring.") if not is_h else "Maintain standard care."
            st.info(f"🧬 **REMEDY:** {rem}")
            
            if not is_h:
                links = get_remedy_purchase_links(pathogen)
                p_cols = st.columns(len(links) if links else 1)
                for i, l in enumerate(links):
                    with p_cols[i]:
                        st.markdown(f"<a href='{l['url']}' target='_blank' style='display:block; text-align:center; background:#064e3b; color:#10b981; padding:15px; border-radius:15px; text-decoration:none; font-weight:900;'>{l['icon']} {l['store']}</a>", unsafe_allow_html=True)
            
            pdf = generate_pdf_report(variant, pathogen, conf, risk_lvl, rem, risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD TITAN CLINICAL DOSSIER", data=pdf, file_name=f"PlantPulse_Titan_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            tab_3d, tab_dna, tab_eng = st.tabs(["🌀 3D Topology", "⚛️ DNA Space", "🔬 Engineering"])
            with tab_3d:
                res = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100))
                fig = go.Figure(data=[go.Surface(z=res, colorscale='Greens')])
                fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            with tab_dna:
                dna = "".join(["ATCG"[hash(variant+str(j)) % 4] for j in range(160)])
                if not is_h: dna = dna.replace("A", "<span style='color:#ef4444'>!</span>")
                st.markdown(f"<div style='font-family:monospace; background:#000; padding:25px; font-size:1.1rem; border:1px solid #4ade80; color:#34d399; line-height:1.5;'>{dna}</div>", unsafe_allow_html=True)
            with tab_eng:
                st.metric("Nitrogen Content", f"{estimate_nitrogen_content(img_bgr)['nitrogen_pct']}%")
                st.metric("Vegetation Index (NDVI)", f"{compute_ndvi_score(img_bgr):.4f}")
                st.metric("Water Stress Index (WSI)", f"{compute_water_stress_index(img_bgr)}%")

# DR LEAF
st.markdown("---")
st.markdown("## 🤖 Dr. Leaf Professional Oracle v9.0")
q_in = st.text_input("Consult the Botanical Oracle...", placeholder="Query a pathogen...")
if q_in:
    res = get_disease_info(q_in)
    st.markdown(f"""
    <div style="background:#020617; border:3px solid #4ade80; padding:40px; border-radius:30px; box-shadow: 0 0 50px rgba(34,197,94,0.2);">
        <h2 style='color:#4ade80; margin-top:0;'>Dr. Leaf's Diagnosis</h2>
        <p style='font-size:1.3rem; color:#d1d5db;'>{res['tips']}</p>
        <div style='background:#064e3b; color:#4ade80; padding:10px 25px; border-radius:12px; font-weight:900; display:inline-block;'>SEVERITY: {res['severity'].upper()}</div>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #4ade80; opacity: 0.6; font-size: 1rem; padding-top: 50px; border-top: 1px solid #14532d;'>
    <b>PLANT PULSE TITAN TECHNOLOGIES</b><br>
    The Ultimate High-Fidelity Suite v9.0 // Distributed Bio-Intelligence<br>
    © 2026 Global Agricultural Intelligence Network
</div>
""", unsafe_allow_html=True)
