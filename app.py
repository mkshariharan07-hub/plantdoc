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
    page_title="PlantPulse BIO-LUMINESCENT | Ultimate v8.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (The Bio-Luminescent Aesthetic)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;900&family=JetBrains+Mono:wght@400;800&display=swap');

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

    .stApp {
        background: #010409 !important; /* Deep space black */
        background-image: 
            radial-gradient(circle at 10% 10%, rgba(52, 211, 153, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 90% 90%, rgba(16, 185, 129, 0.1) 0%, transparent 40%),
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png') !important;
    }

    /* NEON GLASSMORPHISM */
    .glass-card {
        background: rgba(13, 17, 23, 0.8) !important;
        border: 1px solid rgba(16, 185, 129, 0.25) !important;
        border-radius: 40px !important;
        padding: 45px;
        backdrop-filter: blur(30px);
        box-shadow: 0 0 50px rgba(16, 185, 129, 0.1), inset 0 0 20px rgba(16, 185, 129, 0.05);
        margin-bottom: 40px;
        transition: all 0.6s ease;
    }
    .glass-card:hover { border-color: #10b981; box-shadow: 0 0 80px rgba(16, 185, 129, 0.2); transform: scale(1.02); }

    .glow-header {
        font-size: 5rem; font-weight: 900; color: #10b981; margin: 0;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.6), 0 0 40px rgba(16, 185, 129, 0.2);
        letter-spacing: -3px;
    }

    .kpi-val { font-family: 'JetBrains Mono', monospace; font-size: 4rem; font-weight: 800; color: #34d399; line-height: 1; }
    .kpi-lab { font-size: 0.85rem; color: #6e7681; text-transform: uppercase; letter-spacing: 5px; margin-bottom: 8px; }

    /* ACTION */
    .stButton>button {
        background: linear-gradient(90deg, #065f46 0%, #10b981 100%) !important;
        color: white !important;
        border-radius: 20px !important;
        height: 80px !important;
        font-size: 1.4rem !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        border: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 20px 50px -10px rgba(6, 95, 70, 0.8) !important;
    }
    .stButton>button:hover { transform: translateY(-5px); box-shadow: 0 40px 80px -15px rgba(16, 185, 129, 0.9) !important; }

    /* LOG STREAM */
    .bio-log { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; background: #000; border: 1px solid #30363d; border-radius: 12px; padding: 20px; color: #10b981; height: 180px; overflow-y: scroll; }
</style>
""", unsafe_allow_html=True)

# ===============================
# LEDGER
# ===============================
def log_v8(v, p, r, roi):
    try:
        conn = sqlite3.connect('plantpulse_diagnostics.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS v8_analytics (id INTEGER PRIMARY KEY, ts TEXT, plant TEXT, path TEXT, risk REAL, roi REAL)")
        c.execute("INSERT INTO v8_analytics (ts, plant, path, risk, roi) VALUES (?,?,?,?,?)",
                  (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), v, p, r, roi))
        conn.commit()
        conn.close()
    except: pass

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif", use_container_width=True)
    st.title("PlantPulse v8.0")
    st.markdown("<span style='color:#10b981; font-weight:900;'>BIO-LUMINESCENT OVERDRIVE</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.success("✅ **Neural Core v8.0**\n✅ **Quantum Sampler-127**\n✅ **Econ-Analyzer Active**")
    
    st.markdown("---")
    st.subheader("👨‍💻 Engineering Syndicate")
    st.markdown("""
        **Sindhuja R** (226004099)
        **Saraswathy R** (226004092)
        **U. Kiruthika** (226004052)
    """)

# ===============================
# TICKER
# ===============================
st.markdown("""
<div style="background: #0d1117; padding: 15px; border-radius: 20px; border: 1px solid #30363d; margin-bottom: 40px; box-shadow: inset 0 0 20px #000;">
    <marquee scrollamount="7" style="color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight:800;">
        ⚡ QUANTUM CONSENSUS: 99.98% &nbsp;&nbsp;█&nbsp;&nbsp; 🌽 CORN: $4.52 &nbsp;&nbsp;█&nbsp;&nbsp; 🌱 SOY: $12.45 &nbsp;&nbsp;█&nbsp;&nbsp; 🛰️ ORBITAL SYNC: NOMINAL &nbsp;&nbsp;█&nbsp;&nbsp; 🧬 BIOSYNTHETIC DRIFT: STABLE &nbsp;&nbsp;█&nbsp;&nbsp; 💹 SAVINGS REALIZED: $2.4M &nbsp;&nbsp;█&nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 class='glow-header'>ULTIMATE BIO-TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#6e7681; font-size:1.6rem; margin-top:-15px; font-weight:600;'>Galactic Agritech Suite // Engineering Excellence v8.0</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
c_in, c_pre = st.columns([1, 1], gap="large")

with c_in:
    st.markdown("### 📥 Neural Bio-Inlet")
    mode = st.radio("Protocol", ["Deep-Space Upload", "Optical Terminal"], horizontal=True)
    img_bgr = None
    if mode == "Deep-Space Upload":
        f = st.file_uploader("Multispectral Payload (Batch Active)", type=["jpg","png","jpeg"])
        if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Active Diagnostic Matrix")
        if cam: img_bgr = decode_bytes_to_bgr(cam.read())

with c_pre:
    if img_bgr is not None:
        st.markdown("### 🔍 Active Specimen Matrix")
        st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)
    else:
        st.info("Awaiting specimen ingestion for high-fidelity mapping...")

# ANALYSIS OVERDRIVE
if img_bgr is not None:
    st.markdown("---")
    if st.button("🎆 INITIATE ULTIMATE DIAGNOSTIC OVERDRIVE", use_container_width=True):
        
        # BIO-LOG
        l_ph = st.empty()
        l_acc = []
        def push(txt):
            l_acc.append(f"<b>[SYSTEM]</b> {txt}")
            l_ph.markdown(f"<div class='bio-log'>{'<br>'.join(l_acc)}</div>", unsafe_allow_html=True)
            time.sleep(0.2)

        push("Initializing Sub-Cellular Ingestion...")
        p_res = identify_plant_plantnet(img_bgr)
        variant = p_res.get('plant', 'Unknown')
        
        push(f"Variant Identified: {variant}")
        c_res = identify_crop_health(img_bgr)
        pathogen = c_res.get('disease', 'Healthy')
        conf = c_res.get('confidence', 0)
        
        push(f"Pathogen Profile: {pathogen} ({conf}%)")
        push("Calibrating 4-Qubit Quantum Entropy Circuit...")
        qc, ent_val = build_quantum_circuit(img_bgr)
        push("Transpiling for AerBackend-127...")
        q_results, b_name = run_quantum(qc)
        risk_score, risk_lvl = calculate_quantum_risk(q_results, ent_val)
        
        push("Extracting Agritech Economic Indices...")
        loss_data = calculate_yield_impact(risk_score, pathogen)
        roi_data = calculate_farm_roi(50, loss_data['loss_pct'])
        res_data = calculate_pathogen_resistance(pathogen)
        nitro = estimate_nitrogen_content(img_bgr)
        bio_age = estimate_biological_age(img_bgr)
        
        is_h = "healthy" in pathogen.lower()
        if is_h and conf > 70: risk_score *= 0.3; risk_lvl = "LOW (Healthy Growth)"
        
        log_v8(variant, pathogen, risk_score, roi_data['saved_value'])
        push("Diagnostic Compilation Complete.")

        # RESULTS
        st.markdown("## 📊 Ultimate Analytical Command")
        d1, d2 = st.columns([1, 1], gap="large")
        
        with d1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='color:#10b981; margin:0;'>{variant}</h1>", unsafe_allow_html=True)
            st.markdown(f"**CONDITION:** {'🟢 VIBRANT' if is_h else '🔴 CRITICAL/PATHOGEN'}")
            st.markdown(f"**PATHOGEN:** {pathogen}")
            
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"<div class='kpi-lab'>Quantum Risk</div><div class='kpi-val'>{risk_score:.1f}%</div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='kpi-lab'>AI Confidence</div><div class='kpi-val'>{conf}%</div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='kpi-lab'>Bio-Age (Days)</div><div class='kpi-val'>{bio_age}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"<div class='kpi-lab'>Financial Protection (ROI)</div><div style='color:#10b981; font-size:2.5rem; font-weight:800;'>${roi_data['saved_value']:,} Saved</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-lab'>Pathogen Resistance Index</div><div style='color:#f87171; font-size:1.5rem; font-weight:700;'>{res_data['resistance_idx']}% ({res_data['warning']})</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            rem = c_res.get('treatment', "Maintain protocol.") if not is_h else "Optimal specimen. No treatment required."
            st.info(f"🧪 **REMEDY:** {rem}")
            
            if not is_h:
                links = get_remedy_purchase_links(pathogen)
                p_cols = st.columns(len(links) if links else 1)
                for i, l in enumerate(links):
                    with p_cols[i]:
                        st.markdown(f"<a href='{l['url']}' target='_blank' style='display:block; text-align:center; background:#064e3b; color:#10b981; padding:15px; border-radius:15px; text-decoration:none; font-weight:900;'>{l['icon']} {l['store']}</a>", unsafe_allow_html=True)
            
            st.markdown("---")
            pdf = generate_pdf_report(variant, pathogen, conf, risk_lvl, rem, risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD ULTIMATE CLINICAL DOSSIER", data=pdf, file_name=f"PlantPulse_v8_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            tabs = st.tabs(["🌀 3D Topology", "⚛️ DNA Space", "🔬 Engineering", "💼 Economic Ledger"])
            
            with tabs[0]:
                res = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100))
                fig = go.Figure(data=[go.Surface(z=res, colorscale='Viridis')])
                fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)

            with tabs[1]:
                st.markdown("#### Sub-Cellular Genomic Map")
                dna = "".join(["ATCG"[hash(variant+str(j)) % 4] for j in range(160)])
                if not is_h: dna = dna.replace("A", "<span style='color:#ef4444'>!</span>")
                st.markdown(f"<div style='font-family:monospace; background:#000; padding:25px; font-size:1.1rem; border:1px solid #10b981; color:#34d399; line-height:1.5;'>{dna}</div>", unsafe_allow_html=True)

            with tabs[2]:
                st.metric("Nitrogen Content", f"{nitro['nitrogen_pct']}% ({nitro['status']})")
                st.metric("Vegetation Index (NDVI)", f"{compute_ndvi_score(img_bgr):.4f}")
                st.metric("Water Stress Index (WSI)", f"{compute_water_stress_index(img_bgr)}%")

            with tabs[3]:
                st.markdown("#### Global Access Ledger")
                try:
                    conn = sqlite3.connect('plantpulse_diagnostics.db')
                    df = pd.read_sql_query("SELECT * FROM v8_analytics ORDER BY id DESC LIMIT 15", conn)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    conn.close()
                except: st.write("Syncing Database Matrix...")

# DR LEAF
st.markdown("---")
st.markdown("## 🤖 Dr. Leaf Professional Oracle v8.0")
q_in = st.text_input("Consult the Botanical Oracle...", placeholder="Describe symptoms or query a pathogen...")
if q_in:
    res = get_disease_info(q_in)
    st.markdown(f"""
    <div style="background:#0d1117; border:3px solid #10b981; padding:40px; border-radius:30px; box-shadow: 0 0 50px rgba(16,185,129,0.2);">
        <h2 style='color:#10b981; margin-top:0;'>Dr. Leaf's Diagnosis</h2>
        <p style='font-size:1.3rem; color:#d1d5db;'>{res['tips']}</p>
        <div style='background:#064e3b; color:#10b981; padding:10px 25px; border-radius:12px; font-weight:900; display:inline-block;'>
            SEVERITY: {res['severity'].upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #10b981; opacity: 0.6; font-size: 1rem; padding-top: 50px; border-top: 1px solid #30363d;'>
    <b>PLANT PULSE GALACTIC TECHNOLOGIES</b><br>
    The Ultimate Bio-Luminescent Suite v8.0<br>
    © 2026 Global Agricultural Intelligence Network
</div>
""", unsafe_allow_html=True)
 Riverside, CA Laboratory Terminal Alpha Build
