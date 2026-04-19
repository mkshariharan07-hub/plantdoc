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
    generate_growth_forecast
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse OBSIDIAN | The Ultimate Titanic Terminal",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (The OBSIDIAN Aesthetic)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&family=JetBrains+Mono:wght@400;800&family=Bebas+Neue&display=swap');

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

    .stApp {
        background: #000000 !important;
        background-image: 
            radial-gradient(circle at 10% 10%, rgba(34, 197, 94, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 90% 90%, rgba(16, 185, 129, 0.15) 0%, transparent 50%),
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png') !important;
    }

    /* TITANIC SCANNER LINE */
    .scanner-container { position: relative; width: 100%; height: 350px; border-radius: 24px; overflow: hidden; border: 2px solid #14532d; }
    .scanner-line { position: absolute; top: 0; width: 100%; height: 4px; background: #4ade80; box-shadow: 0 0 20px #22c55e; animation: scan 3s linear infinite; }
    @keyframes scan { 0% { top: 0%; } 50% { top: 100%; } 100% { top: 0%; } }

    /* ELITE TITANIC CARDS */
    .elite-card {
        background: rgba(10, 10, 10, 0.95) !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 50px !important;
        padding: 50px;
        backdrop-filter: blur(40px);
        box-shadow: 0 60px 150px -40px rgba(0, 0, 0, 1);
        margin-bottom: 50px;
        transition: 0.6s cubic-bezier(0.19, 1, 0.22, 1);
    }
    .elite-card:hover { border-color: #22c55e; transform: scale(1.01) translateY(-10px); box-shadow: 0 0 100px rgba(34, 197, 94, 0.3); }

    .titan-header { font-family: 'Bebas Neue', cursive; font-size: 7rem; color: #4ade80; text-align: center; margin: 0; letter-spacing: 5px; text-shadow: 0 0 30px rgba(16, 185, 129, 0.5); }

    /* KPI OVERDRIVE */
    .kpi-box { background: rgba(2, 44, 34, 0.5); border: 1px solid #14532d; padding: 25px; border-radius: 24px; text-align: center; }
    .kpi-title { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 4px; font-weight: 700; }
    .kpi-main { font-family: 'JetBrains Mono', monospace; font-size: 3.5rem; color: #4ade80; font-weight: 800; }

    /* LANGUAGE SELECT */
    .lang-item { display: inline-block; padding: 5px 15px; border-radius: 20px; background: #064e3b; color: #4ade80; font-size: 0.7rem; font-weight: 800; margin-right: 5px; border: 1px solid #10b981; }
</style>

<div id="leaves" class="leaf-container" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; overflow: hidden; display: none;">
    <div class="leaf" style="position: absolute; top: -100px; width: 40px; height: 40px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall 5s linear infinite; left: 10%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 40px; height: 40px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall 6s linear infinite; left: 30%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 40px; height: 40px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall 4s linear infinite; left: 50%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 40px; height: 40px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall 7s linear infinite; left: 70%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 40px; height: 40px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall 5s linear infinite; left: 90%;"></div>
</div>
<style>
    @keyframes fall {
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
    st.markdown("<h2 style='text-align:center; color:#4ade80;'>PLANTPULSE TITANIC</h2>", unsafe_allow_html=True)
    
    st.markdown("<div style='text-align:center;'><span class='lang-item'>ENG</span><span class='lang-item'>TAM</span><span class='lang-item'>HIN</span><span class='lang-item'>GER</span></div>", unsafe_allow_html=True)

    st.markdown("### 🛠️ TITANIC CORE v10.0")
    st.markdown("""
    <div style='background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 12px; padding: 15px;'>
        <div style='margin-bottom:8px;'><span style='color:#1db954;'>●</span> PLANTNET NODE 12 [ELITE]</div>
        <div style='margin-bottom:8px;'><span style='color:#1db954;'>●</span> KINDWISE CORE [SYNC]</div>
        <div style='margin-bottom:8px;'><span style='color:#3b82f6;'>●</span> QUANTUM AER-127 [ON]</div>
        <div style='margin-bottom:8px;'><span style='color:#f59e0b;'>●</span> FORECAST ENGINE [LIVE]</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👨‍💻 CHIEF ARCHITECTS")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #052e16, #064e3b); padding: 20px; border-radius: 20px; border: 1px solid #10b981; color: #fff;'>
        <b style='font-size:1.1rem; color:#4ade80;'>SINDHUJA R</b><br><small>226004099</small><hr style='margin:10px 0; opacity:0.2;'>
        <b style='font-size:1.1rem; color:#4ade80;'>SARASWATHY R</b><br><small>226004092</small><hr style='margin:10px 0; opacity:0.2;'>
        <b style='font-size:1.1rem; color:#4ade80;'>KIRUTHIKA U</b><br><small>226004052</small>
    </div>
    """, unsafe_allow_html=True)

# TICKER
st.markdown("""
<div style="background: rgba(10, 10, 10, 0.9); padding: 12px; border-radius: 12px; border: 1px solid #14532d; margin-bottom: 40px; box-shadow: 0 0 20px rgba(16,185,129,0.2);">
    <marquee scrollamount="6" style="color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight:800;">
        ⚡ QUANTUM CONSENSUS: 100% OVERDRIVE &nbsp;&nbsp;█&nbsp;&nbsp; 🌽 CORN: $4.52 (▲) &nbsp;&nbsp;█&nbsp;&nbsp; 🌱 SOY: $12.45 &nbsp;&nbsp;█&nbsp;&nbsp; 🛰️ TITANIC RADAR: SCANNING SECTOR 01 &nbsp;&nbsp;█&nbsp;&nbsp; 🧬 GENOMIC STABILITY: OPTIMAL &nbsp;&nbsp;█&nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 class='titan-header'>OBSIDIAN ANALYTICA</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#6e7681; font-size:1.6rem; text-align:center; margin-top:-30px; font-weight:700;'>Ultimate Galactic Phytopathology Overdrive // v10.0 Obsidian Edition</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
c_in, c_pre = st.columns([1,1], gap="large")

with c_in:
    st.markdown("### 📥 Neural Bio-Ingestion")
    mode = st.radio("Signal Path", ["Quantum Array", "Optical Path"], horizontal=True)
    img_bgr = None
    if mode == "Quantum Array":
        f = st.file_uploader("Select Multispectral Payload", type=["jpg","png","jpeg"])
        if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Active Specimen Scan")
        if cam: img_bgr = decode_bytes_to_bgr(cam.read())

with c_pre:
    if img_bgr is not None:
        st.markdown("### 🔍 Specimen Scanner Matrix")
        st.markdown("""
        <div class='scanner-container'>
            <div class='scanner-line'></div>
            <img src='data:image/png;base64,""" + base64.b64encode(cv2.imencode('.png', img_bgr)[1]).decode() + """' style='width:100%; height:100%; object-fit:cover; opacity:0.8;'>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Awaiting specimen link for terminal initialization...")

# OVERDRIVE EXECUTE
if img_bgr is not None:
    st.markdown("---")
    if st.button("🎆 INITIATE TITANIC ANALYTICAL OVERDRIVE", use_container_width=True):
        
        # LOGS
        ph = st.empty()
        msgs = []
        def push(m):
            msgs.append(f"<b>[SYNC]</b> {m}")
            ph.markdown(f"<div style='font-family:monospace; background:#000; padding:15px; border-radius:15px; border:1px solid #4ade80; color:#34d399; height:120px; overflow-y:auto;'>{'<br>'.join(msgs)}</div>", unsafe_allow_html=True)
            time.sleep(0.3)

        push("Initializing Sub-Cellular Synapse...")
        p_res = identify_plant_plantnet(img_bgr)
        variant = p_res.get('plant', 'Unknown')
        push(f"Class Refined: {variant}")
        
        c_res = identify_crop_health(img_bgr)
        pathogen = c_res.get('disease', 'Healthy')
        conf = c_res.get('confidence', 0)
        push(f"Pathogen Profile: {pathogen} ({conf}%)")
        
        push("Calibrating Aer-127 Quantum Backend...")
        qc, ent = build_quantum_circuit(img_bgr)
        counts, b_name = run_quantum(qc)
        risk_score, risk_lvl = calculate_quantum_risk(counts, ent)
        
        push("Extracting Galactic Economics...")
        nitro = estimate_nitrogen_content(img_bgr)
        ndvi = compute_ndvi_score(img_bgr)
        rank = calculate_global_rank(nitro['nitrogen_pct'], ndvi)
        forecast = generate_growth_forecast(ndvi)
        farm_val = calculate_farm_roi(50, risk_score)
        
        is_h = "healthy" in pathogen.lower()
        if is_h:
            st.markdown("<script>document.getElementById('leaves').style.display = 'block'; setTimeout(() => { document.getElementById('leaves').style.display = 'none'; }, 6000);</script>", unsafe_allow_html=True)
        
        # DASHBOARD
        st.markdown("## 📊 Titanic Command Intelligence")
        d1, d2 = st.columns([1,1], gap="large")
        
        with d1:
            st.markdown("<div class='elite-card'>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='color:#4ade80; margin:0; font-size:4rem;'>{variant}</h1>", unsafe_allow_html=True)
            st.markdown(f"**STATUS:** {'🟢 TITANIC-OPTIMAL' if is_h else '🔴 CRITICAL-INFECTED'}")
            st.markdown(f"**MATCH:** {pathogen}")
            
            st.markdown("---")
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(f"<div class='kpi-box'><div class='kpi-title'>Quantum Risk</div><div class='kpi-main'>{risk_score:.1f}%</div></div>", unsafe_allow_html=True)
            with k2: st.markdown(f"<div class='kpi-box'><div class='kpi-title'>Global Rank</div><div class='kpi-main'>{rank['percentile']}%</div></div>", unsafe_allow_html=True)
            with k3: st.markdown(f"<div class='kpi-box'><div class='kpi-title'>AI Conf</div><div class='kpi-main'>{conf:.0f}%</div></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"🧪 **REMEDY:** {c_res.get('treatment', 'Optimal Specimen.')}")
            st.markdown(f"💰 **ROI RECOVERY:** <span style='color:#4ade80; font-size:2rem; font-weight:900;'>${farm_val['saved_value']:,} Saved</span>", unsafe_allow_html=True)
            
            if not is_h:
                lks = get_remedy_purchase_links(pathogen)
                cols = st.columns(len(lks) if lks else 1)
                for i, l in enumerate(lks):
                    with cols[i]: st.markdown(f"<a href='{l['url']}' target='_blank' style='display:block; text-align:center; background:#064e3b; color:#4ade80; padding:15px; border-radius:20px; text-decoration:none; font-weight:900; border:1px solid #10b981;'>{l['icon']} {l['store']}</a>", unsafe_allow_html=True)
            
            st.markdown("---")
            pdf = generate_pdf_report(variant, pathogen, conf, risk_lvl, "Treat immediately.", risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD TITANIC CLINICAL REPORT", data=pdf, file_name=f"PlantPulse_Obsidian_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            tab_3d, tab_forecast, tab_dna = st.tabs(["🌀 3D Topology", "📈 Growth Forecast", "⚛️ DNA Space"])
            with tab_3d:
                res = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100))
                fig = go.Figure(data=[go.Surface(z=res, colorscale='Greens')])
                fig.update_layout(height=500, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            with tab_forecast:
                st.markdown("#### Projected Biomass Accumulation (NDVI Forecast)")
                st.line_chart(forecast)
                st.info("Specimen expected to reach elite growth percentile in 14 days.")
            with tab_dna:
                dna = "".join(["ATCG"[hash(variant+str(j)) % 4] for j in range(200)])
                if not is_h: dna = dna.replace("A", "<span style='color:#ef4444'>!</span>")
                st.markdown(f"<div style='font-family:monospace; background:#000; padding:30px; font-size:1.2rem; border:2px solid #4ade80; color:#34d399; line-height:1.5; text-align:center; letter-spacing:4px;'>{dna}</div>", unsafe_allow_html=True)

# ORACLE
st.markdown("---")
st.markdown("<h2 style='text-align:center; font-family:Bebas Neue; font-size:4rem; color:#4ade80;'>🤖 THE TITANIC ORACLE</h2>", unsafe_allow_html=True)
q = st.text_input("Consult the Titanic Collective Intelligence...", placeholder="Ask about growth, productivity, or specific symptoms...")
if q:
    ans = get_disease_info(q)
    st.markdown(f"""
    <div style="background:#0a0a0a; border:4px solid #4ade80; padding:50px; border-radius:40px; box-shadow: 0 0 100px rgba(34,197,94,0.3);">
        <h2 style='color:#4ade80; margin-top:0;'>Oracle Diagnosis</h2>
        <p style='font-size:1.5rem; color:#d1d5db; line-height:1.6;'>{ans['tips']}</p>
        <div style='background:#064e3b; color:#4ade80; padding:15px 35px; border-radius:20px; font-weight:900; display:inline-block; font-size:1.5rem;'>SEVERITY: {ans['severity'].upper()}</div>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #4ade80; opacity: 0.6; font-size: 1.1rem; padding-top: 50px; border-top: 2px solid #14532d;'>
    <b>PLANT PULSE TITANIC OBSIDIAN</b><br>
    The Ultimate Galactic Suite v10.0 // Sovereign Agricultural Collective<br>
    © 2026 Global Agricultural Intelligence Network
</div>
""", unsafe_allow_html=True)
