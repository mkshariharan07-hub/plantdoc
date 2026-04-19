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
    classify_pathogen_severity, calculate_global_rank,
    generate_growth_forecast, calculate_molecular_stress_index,
    predict_harvest_revenue, calculate_degrade_velocity,
    calculate_treatment_efficacy, estimate_npk_balance
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse ZENITH | Ultimate Biosphere Terminal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# ZENITH STYLE OVERRIDES
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@800&family=Michroma&family=Space+Grotesk:wght@300;700&family=JetBrains+Mono&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }

    .stApp {
        background: #010204 !important;
        background-image: 
            radial-gradient(circle at 10% 10%, rgba(34, 197, 94, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 90% 90%, rgba(16, 185, 129, 0.15) 0%, transparent 50%),
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png') !important;
    }

    /* THE ZENITH HEADER */
    .zenith-title { font-family: 'Syne', sans-serif; font-size: 8rem; font-weight: 800; color: #4ade80; text-align: center; margin: 0; letter-spacing: -8px; line-height: 0.8; text-transform: uppercase; text-shadow: 0 0 50px rgba(74, 222, 128, 0.4); }
    .zenith-tag { font-family: 'Michroma', sans-serif; font-size: 1rem; color: #10b981; text-align: center; letter-spacing: 12px; margin-top: 10px; opacity: 0.8; }

    /* ULTIMATE ZENITH CARDS */
    .zenith-card {
        background: rgba(10, 10, 10, 0.95) !important;
        border: 2px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 60px !important;
        padding: 65px;
        backdrop-filter: blur(50px);
        box-shadow: 0 100px 300px -50px rgba(0, 0, 0, 1);
        margin-bottom: 60px;
        transition: 0.8s;
    }
    .zenith-card:hover { border-color: #22c55e; box-shadow: 0 0 150px rgba(34, 197, 94, 0.2); }

    /* CORE STATS */
    .zen-stat { background: #000; border: 1px solid #14532d; padding: 30px; border-radius: 30px; text-align: center; }
    .zen-val { font-family: 'JetBrains Mono', monospace; font-size: 4rem; color: #4ade80; font-weight: 900; }
    .zen-lab { font-family: 'Michroma', sans-serif; font-size: 0.7rem; color: #6e7681; text-transform: uppercase; letter-spacing: 4px; margin-bottom: 5px; }

    /* SCANNER ZENITH */
    .scanner-z { position: absolute; width: 100%; height: 10px; background: linear-gradient(transparent, #4ade80, transparent); box-shadow: 0 0 40px #22c55e; animation: scan-z 4s ease-in-out infinite; }
    @keyframes scan-z { 0%, 100% { top: 0%; } 50% { top: 100%; } }
</style>

<div id="leaves_zenith" class="leaf-container" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; overflow: hidden; display: none;">
    <div class="leaf" style="position: absolute; top: -100px; width: 60px; height: 60px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall-zenith 6s linear infinite; left: 10%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 60px; height: 60px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall-zenith 4s linear infinite; left: 40%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 60px; height: 60px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall-zenith 7s linear infinite; left: 70%;"></div>
</div>
<style>
    @keyframes fall-zenith {
        0% { transform: translateY(-100px) rotate(0deg); }
        100% { transform: translateY(110vh) rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif", use_container_width=True)
    st.markdown("<h2 style='text-align:center; color:#4ade80; font-family:Syne;'>ZENITH INTERFACE</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🛠️ ZENITH CORE INFRA")
    st.markdown("""
    <div style='background:rgba(16, 185, 129, 0.05); padding:15px; border-radius:15px; border:1px solid #10b981;'>
        🟢 PLANTNET-50 NODE [SYN]<br>
        🟢 QUANTUM AER-127 [ON]<br>
        🟢 BIO-ECONOMY [ACTIVE]<br>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👨‍💻 CHIEF ARCHITECTS")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #020617, #064e3b); padding: 25px; border-radius: 24px; border: 1px solid #10b981; color: #fff;'>
        <b style='font-size:1.1rem; color:#4ade80; font-family:Syne;'>SINDHUJA R</b><br><small>226004099</small><hr style='margin:12px 0; opacity:0.1;'>
        <b style='font-size:1.1rem; color:#4ade80; font-family:Syne;'>SARASWATHY R</b><br><small>226004092</small><hr style='margin:12px 0; opacity:0.1;'>
        <b style='font-size:1.1rem; color:#4ade80; font-family:Syne;'>KIRUTHIKA U</b><br><small>226004052</small>
    </div>
    """, unsafe_allow_html=True)

# TICKER
st.markdown("""
<div style="background: #000; padding: 12px; border-radius: 20px; border: 1px solid #065f46; margin-bottom: 50px;">
    <marquee scrollamount="6" style="color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight:800;">
        ⚡ ZENITH SYNC: 100% OVERDRIVE &nbsp;&nbsp;█&nbsp;&nbsp; 💹 SAVINGS REALIZED: +$8.4B &nbsp;&nbsp;█&nbsp;&nbsp; 🧬 MOLECULAR STABILITY: 99.4% &nbsp;&nbsp;█&nbsp;&nbsp; 🛰️ ZENITH RADAR: ACTIVE &nbsp;&nbsp;█&nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 class='zenith-title'>ZENITH ANALYTICA</h1>", unsafe_allow_html=True)
st.markdown("<p class='zenith-tag'>SUPREME BIOSCIENCE TERMINAL // ULTIMATE ZENITH</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
c_i, c_p = st.columns([1,1], gap="large")

with c_i:
    st.markdown("### 📥 Bio-Signature Ingestion")
    mode = st.radio("Signal Source", ["Quantum Uplink", "Optical Path"], horizontal=True)
    img_bgr = None
    if mode == "Quantum Uplink":
        f = st.file_uploader("Select Multispectral Payload", type=["jpg","png","jpeg"])
        if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Active Specimen Zenith Scan")
        if cam: img_bgr = decode_bytes_to_bgr(cam.read())

with c_p:
    if img_bgr is not None:
        st.markdown("### 🔍 Specimen Scanner Matrix")
        st.markdown("""
        <div style='position:relative; width:100%; height:400px; border-radius:40px; overflow:hidden; border:3px solid #064e3b;'>
            <div class='scanner-z'></div>
            <img src='data:image/png;base64,""" + base64.b64encode(cv2.imencode('.png', img_bgr)[1]).decode() + """' style='width:100%; height:100%; object-fit:cover;'>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Awaiting specimen link for zenith terminal initialization...")

# OVERDRIVE EXECUTE
if img_bgr is not None:
    st.markdown("---")
    if st.button("🎆 INITIATE SUPREME ZENITH OVERDRIVE", use_container_width=True):
        
        # LOGS
        ph = st.empty()
        m = []
        def push(txt):
            m.append(f"<b>[ZENITH]</b> {txt}")
            ph.markdown(f"<div style='font-family:JetBrains Mono; background:#000; padding:20px; border-radius:30px; border:1px solid #4ade80; color:#34d399; height:120px; overflow-y:auto;'>{'<br>'.join(m)}</div>", unsafe_allow_html=True)
            time.sleep(0.2)

        push("Initializing Molecular Sync...")
        p_res = identify_plant_plantnet(img_bgr)
        c_res = identify_crop_health(img_bgr)
        variant = c_res.get('plant', 'Specimen Gamma')
        pathogen = c_res.get('disease', 'Healthy Spectrum')
        conf = c_res.get('confidence', 0)
        sev = c_res.get('severity_score', 0)
        
        push(f"Class Refined: {variant}")
        push("Calibrating Aer-127 Quantum Backend...")
        qc, ent = build_quantum_circuit(img_bgr)
        counts, b_n = run_quantum(qc)
        risk_score, r_lvl = calculate_quantum_risk(counts, ent)
        
        push("Synthesizing Bio-Metrics...")
        n_v = compute_ndvi_score(img_bgr)
        rank = calculate_global_rank(estimate_nitrogen_content(img_bgr)["nitrogen_pct"], n_v)
        eff = calculate_treatment_efficacy(sev, 20)
        npk = estimate_npk_balance(img_bgr)
        rev = predict_harvest_revenue(50, rank['percentile'])
        
        is_h = "healthy" in pathogen.lower()
        if is_h:
            st.markdown("<script>document.getElementById('leaves_zenith').style.display = 'block'; setTimeout(() => { document.getElementById('leaves_zenith').style.display = 'none'; }, 8000);</script>", unsafe_allow_html=True)
        
        # DASHBOARD
        st.markdown("## 📊 Zenith Intelligence Dashboard")
        d1, d2 = st.columns([1, 1], gap="large")
        
        with d1:
            st.markdown("<div class='zenith-card'>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='color:#4ade80; margin:0; font-family:Syne; font-size:5rem;'>{variant.upper()}</h1>", unsafe_allow_html=True)
            st.markdown(f"**MOLECULAR STATE:** {'🟢 SUPREME' if is_h else '🔴 DEGRADED'}")
            st.markdown(f"**PATHOGEN:** {pathogen}")
            
            st.markdown("---")
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(f"<div class='zen-stat'><div class='zen-lab'>Quantum Risk</div><div class='zen-val'>{risk_score:.1f}%</div></div>", unsafe_allow_html=True)
            with k2: st.markdown(f"<div class='zen-stat'><div class='zen-lab'>Severity</div><div class='zen-val' style='color:#f87171;'>{sev}%</div></div>", unsafe_allow_html=True)
            with k3: st.markdown(f"<div class='zen-stat'><div class='zen-lab'>Efficacy</div><div class='zen-val' style='color:#3b82f6;'>{eff}%</div></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"💰 **PREDICTED REVENUE:** <span style='color:#4ade80; font-size:2rem; font-weight:900;'>${rev:,}</span>", unsafe_allow_html=True)
            st.markdown(f"🧬 **NPK BALANCE:** N:{npk['n']}% | P:{npk['p']}% | K:{npk['k']}%")
            
            st.markdown("---")
            pdf = generate_pdf_report(variant, pathogen, conf, r_lvl, "Treat immediately.", risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD ZENITH CLINICAL DOSSIER", data=pdf, file_name=f"PlantPulse_Zenith_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            st.markdown("<div class='zenith-card' style='padding:40px;'>", unsafe_allow_html=True)
            tabs = st.tabs(["🌀 Zenith Topology", "🌍 Threat Matrix", "📈 Growth Forecast"])
            with tabs[0]:
                res_gray = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100))
                fig = go.Figure(data=[go.Surface(z=res_gray, colorscale='Viridis')])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            with tabs[1]:
                pts = pd.DataFrame(np.random.randn(50, 2) / [20, 20] + [37.77, -122.42], columns=['lat', 'lon'])
                st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/dark-v11', initial_view_state=pdk.ViewState(latitude=37.77, longitude=-122.42, zoom=10, pitch=50),
                    layers=[pdk.Layer('HexagonLayer', data=pts, get_position='[lon, lat]', radius=500, extruded=True, elevation_scale=50)]))
            with tabs[2]:
                st.line_chart(generate_growth_forecast(n_v))
            st.markdown("</div>", unsafe_allow_html=True)

# ORACLE
st.markdown("---")
st.markdown("<h2 style='text-align:center; font-family:Syne; font-size:5rem; color:#4ade80;'>🤖 THE ZENITH ORACLE</h2>", unsafe_allow_html=True)
q = st.text_input("Consult the Titanic Collective Intelligence...", placeholder="Ask the Oracle about growth, productivity, or specific symptoms...")
if q:
    ans = get_disease_info(q)
    st.markdown(f"""
    <div style="background:#0a0a0a; border:4px solid #4ade80; padding:60px; border-radius:50px; box-shadow: 0 0 120px rgba(34,197,94,0.4);">
        <h2 style='color:#4ade80; margin-top:0; font-family:Syne;'>Oracle Wisdom</h2>
        <p style='font-size:1.6rem; color:#d1d5db; line-height:1.7; font-family:Space Grotesk;'>{ans['tips']}</p>
        <div style='background:#064e3b; color:#4ade80; padding:15px 40px; border-radius:24px; font-weight:900; display:inline-block; font-size:1.6rem; font-family:Michroma; border:2px solid #10b981;'>SEVERITY: {ans['severity'].upper()}</div>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #4ade80; opacity: 0.6; font-size: 1.1rem; padding-top: 60px; border-top: 2px solid #14532d; font-family:Space Grotesk;'>
    <b>PLANT PULSE ZENITH SUPREME</b><br>
    The Ultimate High-Fidelity Zenith Terminal // Global Agritech Collective<br>
    © 2026 Sovereign Biological Collective
</div>
""", unsafe_allow_html=True)
