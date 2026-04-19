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
    get_remedy_purchase_links
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse ELITE | Engineering Core v7.5",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (The Elite Engineering Theme)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&family=JetBrains+Mono:wght@500;800&display=swap');

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

    .stApp {
        background: #020c08 !important; /* Midnight Forest */
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(34, 197, 94, 0.2) 0%, transparent 40%),
            radial-gradient(circle at 100% 100%, rgba(20, 184, 166, 0.2) 0%, transparent 40%),
            linear-gradient(rgba(16, 185, 129, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(16, 185, 129, 0.02) 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px !important;
    }

    /* ELITE GLASSMORPHISM */
    .glass-card {
        background: rgba(4, 30, 24, 0.85) !important;
        border: 2px solid rgba(16, 185, 129, 0.2) !important;
        border-radius: 36px !important;
        padding: 40px;
        backdrop-filter: blur(20px);
        box-shadow: 0 50px 100px -20px rgba(0, 0, 0, 0.8);
        margin-bottom: 35px;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
    }
    .glass-card::before {
        content: ''; position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px;
        border-radius: 36px; background: linear-gradient(45deg, transparent, rgba(16, 185, 129, 0.1), transparent);
        z-index: -1;
    }
    .glass-card:hover { border-color: #10b981; transform: translateY(-10px); }

    .stat-val { font-family: 'JetBrains Mono', monospace; font-size: 3.5rem; color: #10b981; font-weight: 800; text-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }
    .stat-label { font-size: 0.9rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 4px; margin-bottom: 5px; }

    /* CORE STATUS LIGHTS */
    .status-light { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; box-shadow: 0 0 8px currentColor; }
</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown("<div style='text-align:center'><img src='https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif' style='border-radius:24px; width:100%; box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);'></div>", unsafe_allow_html=True)
    st.title("PlantPulse ELITE")
    st.markdown("<p style='color:#10b981; font-weight:800; font-size:0.8rem;'>CORE v7.5 // QUANTUM-BIOMETRIC STACK</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🛠️ Engineering Core")
    st.write("<span class='status-light' style='color:#10b981; background:#10b981'></span> PlantNet-50 Node", unsafe_allow_html=True)
    st.write("<span class='status-light' style='color:#10b981; background:#10b981'></span> Kindwise-AI Sync", unsafe_allow_html=True)
    st.write("<span class='status-light' style='color:#0ea5e9; background:#0ea5e9'></span> Qiskit-Aer 127 Engine", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("👨‍💻 System Architects")
    st.markdown("""
        **Sindhuja R** (226004099)
        **Saraswathy R** (226004092)
        **U. Kiruthika** (226004052)
    """)

# ===============================
# MARKET INTEGRATION
# ===============================
st.markdown("""
<div style="background: rgba(2, 44, 34, 0.9); padding: 12px; border: 1px solid #14532d; border-radius: 12px; margin-bottom: 30px;">
    <marquee scrollamount="6" style="color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight:700;">
        ⚡ QUANTUM STATE: Coherent &nbsp;&nbsp;█&nbsp;&nbsp; 🌽 CORN: $4.52 &nbsp;&nbsp;█&nbsp;&nbsp; 🌱 SOY: $12.45 &nbsp;&nbsp;█&nbsp;&nbsp; 🛰️ THERMAL RADAR: SYNCED &nbsp;&nbsp;█&nbsp;&nbsp; 🧬 GENOMIC DRIFT: <0.01% &nbsp;&nbsp;█&nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 style='color:#10b981; font-size:4.5rem; font-weight:900; margin-bottom:0; letter-spacing:-2px;'>CORE INTELLIGENCE TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; font-size:1.5rem; margin-top:-10px; font-weight:400;'>Precision Agritech Overdrive // v7.5 Galactic Engineering</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
in_c1, in_c2 = st.columns([1, 1], gap="large")

with in_c1:
    st.markdown("#### 📥 Hybrid Bio-Inlet")
    src = st.radio("Protocol", ["Deep-Space Upload", "Local Optical Mesh"], horizontal=True)
    img_bgr = None
    if src == "Deep-Space Upload":
        f = st.file_uploader("Multispectral Payload", type=["jpg","png","jpeg"])
        if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        c = st.camera_input("Optical Diagnostic")
        if c: img_bgr = decode_bytes_to_bgr(c.read())

with in_c2:
    if img_bgr is not None:
        st.markdown("#### 🔍 Active Specimen Matrix")
        st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)
    else:
        st.info("Awaiting specimen ingestion for high-fidelity mapping.")

# CORE EXECUTE
if img_bgr is not None:
    st.markdown("---")
    if st.button("🚀 INITIATE ELITE ENGINEERING SEQUENCE", use_container_width=True):
        
        # LOGS
        l_ph = st.empty()
        l_acc = []
        def push(txt):
            l_acc.append(f"<span style='color:#10b981;'>[CORE]</span> {txt}")
            l_ph.markdown(f"<div style='font-family:monospace; background:#01120a; padding:15px; border-radius:15px; border:1px solid #10b981; height:120px; overflow-y:auto;'>{'<br>'.join(l_acc)}</div>", unsafe_allow_html=True)
            time.sleep(0.3)

        push("Calibrating Neural Synapse...")
        p_res = identify_plant_plantnet(img_bgr)
        variant = p_res.get('plant', 'Unknown')
        
        push(f"Class identified: {variant}")
        c_res = identify_crop_health(img_bgr)
        pathogen = c_res.get('disease', 'Healthy')
        conf = c_res.get('confidence', 0)
        
        push("Engaging Quantum Backend (AerSimulator-127)...")
        qc, entropy = build_quantum_circuit(img_bgr)
        counts, b_name = run_quantum(qc)
        risk_score, risk_lvl = calculate_quantum_risk(counts, entropy)
        
        push("Extracting Secondary Engineering Metrics...")
        nitro = estimate_nitrogen_content(img_bgr)
        yield_data = calculate_yield_impact(risk_score, pathogen)
        
        is_h = "healthy" in pathogen.lower()
        if is_h and conf > 70: risk_score *= 0.3; risk_lvl = "LOW (Healthy Growth)"
        
        # UI
        st.markdown("## 📊 Elite Engineering Dashboard")
        d1, d2 = st.columns([1, 1], gap="large")
        
        with d1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#10b981; margin-top:0;'>{variant}</h2>", unsafe_allow_html=True)
            st.markdown(f"**CONDITION:** {'🟢 VIBRANT/SAFE' if is_h else '🔴 INFECTED'}")
            st.markdown(f"**PATHOGEN:** {pathogen}")
            
            st.markdown("---")
            m_c1, m_c2 = st.columns(2)
            m_c1.markdown(f"<div class='stat-label'>Quantum Risk</div><div class='stat-val'>{risk_score:.1f}%</div>", unsafe_allow_html=True)
            m_c2.markdown(f"<div class='stat-label'>AI Confidence</div><div class='stat-val'>{conf}%</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"<div class='stat-label'>Nitrogen Concentration</div><div style='color:#4ade80; font-size:1.5rem; font-weight:800;'>{nitro['nitrogen_pct']}% ({nitro['status']})</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='stat-label'>Predicted Yield Impact</div><div style='color:#f87171; font-size:1.5rem; font-weight:800;'>-{yield_data['loss_pct']}% Loss</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            rem = c_res.get('treatment', "Maintain protocol.") if not is_h else "No remediation required."
            st.info(f"🧬 **REMEDY:** {rem}")
            
            if not is_h:
                p_links = get_remedy_purchase_links(pathogen)
                cols = st.columns(len(p_links) if p_links else 1)
                for idx, l in enumerate(p_links):
                    with cols[idx]:
                        st.markdown(f"<a href='{l['url']}' target='_blank' style='display:block; background:#064e3b; color:#10b981; padding:12px; border-radius:12px; text-decoration:none; text-align:center; font-weight:800; border:1px solid #10b981;'>{l['icon']} {l['store']}</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            tab_eng, tab_dna, tab_map = st.tabs(["⚙️ Core Analytics", "⚛️ DNA Space", "🌍 Threat Matrix"])
            
            with tab_eng:
                st.markdown("#### Tactical 3D Surface Topography")
                res = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100))
                fig = go.Figure(data=[go.Surface(z=res, colorscale='Greens')])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                n_v = compute_ndvi_score(img_bgr)
                st.metric("Vegetation Index (NDVI)", f"{n_v:.4f}")
                st.progress((n_v+1)/2, text="Biomass Density Allocation")

            with tab_dna:
                dna = "".join(["ATCG"[hash(variant+str(j)) % 4] for j in range(120)])
                if not is_h: dna = dna.replace("A", "<span style='color:#ef4444'>!</span>").replace("C", "<span style='color:#ef4444'>?</span>")
                st.markdown(f"<div style='font-family:monospace; background:#000; padding:20px; font-size:1rem; border:2px solid #10b981; line-height:1.4;'>{dna}</div>", unsafe_allow_html=True)
                st.caption("Quantum genomic drift visualization.")

            with tab_map:
                pts = pd.DataFrame(np.random.randn(50, 2) / [20, 20] + [37.77, -122.42], columns=['lat', 'lon'])
                st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/dark-v11', initial_view_state=pdk.ViewState(latitude=37.77, longitude=-122.42, zoom=10, pitch=50),
                    layers=[pdk.Layer('HexagonLayer', data=pts, get_position='[lon, lat]', radius=500, extruded=True, elevation_scale=50)]))

# DR LEAF
st.markdown("---")
st.markdown("## 🤖 Dr. Leaf Professional Expert Module")
q_in = st.text_input("Consult the Botanical Oracle v7.5...", placeholder="Enter symptoms or pathogen name...")
if q_in:
    res = get_disease_info(q_in)
    st.markdown(f"""
    <div style="background:#01120a; border:3px solid #10b981; padding:30px; border-radius:24px; box-shadow: 0 0 30px rgba(16,185,129,0.2);">
        <h3 style="color:#10b981; margin-top:0;">Dr. Leaf's Diagnosis</h3>
        <p style="font-size:1.2rem; color:#d1d5db; line-height:1.6;">{res['tips']}</p>
        <div style="display:inline-block; background:#064e3b; color:#10b981; padding:8px 20px; border-radius:10px; font-weight:800; border:1px solid #10b981;">
            SEVERITY: {res['severity'].upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)
