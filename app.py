import streamlit as st
import cv2
import numpy as np
import os
import base64
import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk
import sqlite3
import time
from io import BytesIO
from dotenv import load_dotenv

from utils import (
    identify_plant_plantnet, identify_crop_health, get_disease_info,
    build_quantum_circuit, run_quantum, calculate_quantum_risk,
    generate_pdf_report, get_perenual_care_info, generate_pathogen_mask,
    decode_bytes_to_bgr, compute_ndvi_score, compute_water_stress_index,
    estimate_nitrogen_content, calculate_farm_roi, estimate_biological_age,
    get_remedy_purchase_links, calculate_global_rank, generate_growth_forecast,
    calculate_treatment_efficacy, estimate_npk_balance,
    get_live_photoperiod, estimate_carbon_sequestration, get_health_gauge_color,
    calculate_degrade_velocity, calculate_molecular_stress_index
)

load_dotenv()

st.set_page_config(
    page_title="PlantDoc | Zenith Bioscience Terminal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────
#  ZENITH SUPREME CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Michroma&family=Space+Grotesk:wght@300;400;700&family=JetBrains+Mono:wght@400;800&display=swap');

html, body, [class*="css"] { font-family:'Space Grotesk', sans-serif !important; }

/* BACKGROUND - ENHANCED ZENITH GREEN */
.stApp {
    background: #010203 !important;
    background-image:
        radial-gradient(circle at 5% 5%, rgba(16,185,129,0.18) 0%, transparent 40%),
        radial-gradient(circle at 95% 95%, rgba(52,211,153,0.15) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(6,78,59,0.08) 0%, transparent 60%),
        url('https://www.transparenttextures.com/patterns/black-linen.png') !important;
}

/* HEADER */
.title-zen {
    font-family:'Syne',sans-serif; font-size:9.5rem; font-weight:800;
    background: linear-gradient(180deg,#ffffff 0%,#10b981 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    text-align:center; margin:0; letter-spacing:-12px; line-height:.8;
    filter: drop-shadow(0 0 30px rgba(16,185,129,0.4));
}
.subtitle-zen {
    font-family:'Michroma',sans-serif; font-size:.8rem; letter-spacing:16px;
    color:#34d399; text-align:center; margin-top:20px; opacity:.9;
    text-shadow: 0 0 10px rgba(52,211,153,0.5);
}

/* GLASS CARDS */
.gcard {
    background:rgba(8,12,18,.96);
    border:2px solid rgba(16,185,129,.45);
    border-radius:52px; padding:60px;
    backdrop-filter:blur(80px);
    box-shadow:0 100px 250px -40px rgba(0,0,0,1), 
               inset 0 0 40px rgba(16,185,129,.05);
    margin-bottom:50px;
    transition:all .6s cubic-bezier(0.23, 1, 0.32, 1);
}
.gcard:hover { 
    border-color:#34d399; 
    box-shadow:0 0 120px rgba(16,185,129,.25);
    transform: translateY(-5px);
}

/* NAMES */
.plant-name {
    font-family:'Syne',sans-serif; font-size:5rem; font-weight:800;
    color:#fff; line-height:.95; margin:0;
    background: linear-gradient(90deg, #10b981, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding-bottom: 10px;
}
.disease-name {
    font-family:'Michroma',sans-serif; font-size:1.6rem; letter-spacing:4px;
    margin-top:20px; padding:16px 32px; border-radius:20px; display:inline-block;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.dis-healthy { background:rgba(16,185,129,.25); color:#a7f3d0; border:2px solid #34d399; }
.dis-infected { background:rgba(239,68,68,.25); color:#fecaca; border:2px solid #ef4444; }

/* SEVERITY BADGES */
.sev-matrix {
    display: flex; gap: 10px; margin-top: 25px;
}
.sev-bit {
    flex: 1; height: 12px; border-radius: 6px; background: #1f2937;
    position: relative; overflow: hidden;
}
.sev-bit.active { background: #10b981; box-shadow: 0 0 15px #10b981; }
.sev-bit.critical { background: #ef4444; box-shadow: 0 0 15px #ef4444; }

/* METRICS */
.mbox {
    background:rgba(1,2,3,.8); border:1px solid #064e3b;
    border-radius:32px; padding:32px; text-align:center;
    transition: .3s;
}
.mbox:hover { border-color: #10b981; background: #020617; }
.mval {
    font-family:'JetBrains Mono',monospace; font-size:3.8rem;
    font-weight:900; line-height:1; letter-spacing: -2px;
}
.mlabel {
    font-family:'Michroma',sans-serif; font-size:.7rem;
    color:#94a3b8; letter-spacing:5px; text-transform:uppercase; margin-bottom:10px;
}

/* REMEDY */
.remedy-block {
    background:linear-gradient(135deg,rgba(6,78,59,.9),rgba(2,6,23,.98));
    border:2px solid #34d399; border-radius:36px; padding:44px;
    font-size:1.3rem; line-height:1.9; color:#f0fdf4;
    box-shadow:inset 0 0 60px rgba(16,185,129,.1);
}

/* SCANNER */
.scn-wrap { 
    position:relative; border-radius:40px; overflow:hidden; 
    border:3px solid #065f46;
    box-shadow: 0 0 40px rgba(16,185,129,0.2);
}
.scn-line { 
    position:absolute; width:100%; height:10px;
    background:linear-gradient(transparent, #34d399, transparent);
    box-shadow:0 0 40px #10b981; 
    animation:scn 3s ease-in-out infinite;
    z-index: 10;
}
@keyframes scn { 0%,100%{top:0%} 50%{top:100%} }

/* TICKER */
.ticker-wrap { background:#000; border:1px solid #064e3b; border-radius:20px; padding:12px; margin-bottom:48px; }

/* SIDEBAR */
.sidebar-stat { background:rgba(16,185,129,.08); border:1px solid #10b981; border-radius:14px; padding:14px; margin-bottom:8px; }
</style>

<!-- FALLING LEAVES -->
<div id="leaves_plantdoc" style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;overflow:hidden;display:none;">
  <div class="lf" style="position:absolute;top:-80px;left:8%;animation:leaf-fall 5s linear infinite;width:50px;height:50px;background:url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') center/contain no-repeat;"></div>
  <div class="lf" style="position:absolute;top:-80px;left:28%;animation:leaf-fall 7s linear infinite;width:45px;height:45px;background:url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') center/contain no-repeat;"></div>
  <div class="lf" style="position:absolute;top:-80px;left:52%;animation:leaf-fall 4.5s linear infinite;width:55px;height:55px;background:url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') center/contain no-repeat;"></div>
  <div class="lf" style="position:absolute;top:-80px;left:74%;animation:leaf-fall 6s linear infinite;width:42px;height:42px;background:url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') center/contain no-repeat;"></div>
  <div class="lf" style="position:absolute;top:-80px;left:90%;animation:leaf-fall 5.5s linear infinite;width:48px;height:48px;background:url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') center/contain no-repeat;"></div>
</div>
<style>
@keyframes leaf-fall {
  0%   { transform:translateY(-80px) rotate(0deg); opacity:1; }
  100% { transform:translateY(110vh) rotate(390deg); opacity:.2; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif", use_container_width=True)

    st.markdown("---")
    st.markdown("### 📡 Live Environmental Telemetry")
    try:
        ph = get_live_photoperiod()
        st.markdown(f"""<div class='sidebar-stat'>
            🌅 <b>SUNRISE:</b> {ph.get('sunrise','N/A')[:8]}<br>
            🌇 <b>SUNSET:</b> {ph.get('sunset','N/A')[:8]}<br>
            ☀️ <b>DAY LENGTH:</b> {ph.get('day_length','N/A')[:8]}
        </div>""", unsafe_allow_html=True)
    except:
        st.info("Environmental sync unavailable.")

    st.markdown("### 🛠️ Zenith Core Infrastructure")
    st.markdown("""<div class='sidebar-stat'>
        🟢 PLANTNET-50 NODE<br>
        🟢 KINDWISE CROP.HEALTH<br>
        🟢 QISKIT AER-127<br>
        🟢 QUANTUM ENTROPY ENGINE<br>
        🟡 PERENUAL CARE API
    </div>""", unsafe_allow_html=True)

    st.markdown("### 👨‍💻 Chief Architects")
    st.markdown("""<div class='sidebar-stat' style='color:#d1fae5;'>
        <b style='color:#4ade80;'>Sindhuja R</b> — 226004099<br>
        <b style='color:#4ade80;'>Saraswathy R</b> — 226004092<br>
        <b style='color:#4ade80;'>Kiruthika U</b> — 226004052
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  TICKER
# ─────────────────────────────────────────────────────────
st.markdown("""<div class='ticker-wrap'>
<marquee scrollamount='5' style='color:#4ade80;font-family:JetBrains Mono,monospace;font-size:.95rem;font-weight:800;'>
  ⚡ QUANTUM CORE: 100% OVERDRIVE &nbsp;█&nbsp;
  🧬 MOLECULAR STABILITY: NOMINAL &nbsp;█&nbsp;
  🛰️ ZENITH RADAR: ACTIVE &nbsp;█&nbsp;
  🌿 PLANTDOC DIAGNOSTIC: ONLINE &nbsp;█&nbsp;
  📡 LIVE TELEMETRY: SYNCED &nbsp;█
</marquee></div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  HERO HEADER
# ─────────────────────────────────────────────────────────
st.markdown("<h1 class='title-zen'>PlantDoc</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-zen'>ZENITH BIOSCIENCE TERMINAL // SUPREME EDITION</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  BIO-INGESTION
# ─────────────────────────────────────────────────────────
st.markdown("---")
ing1, ing2 = st.columns([1, 1], gap="large")

img_bgr = None
with ing1:
    st.markdown("### 📥 Bio-Signature Ingestion")
    src = st.radio("Signal Source", ["Upload Payload", "Live Optical Scan"], horizontal=True)
    if src == "Upload Payload":
        f = st.file_uploader("Select Multispectral Specimen Payload", type=["jpg","jpeg","png"])
        if f:
            img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Live Optical Scan")
        if cam:
            img_bgr = decode_bytes_to_bgr(cam.read())

with ing2:
    if img_bgr is not None:
        st.markdown("### 🔬 Zenith Scanner Matrix")
        enc_img = base64.b64encode(cv2.imencode('.png', img_bgr)[1]).decode()
        st.markdown(f"""
        <div class='scn-wrap' style='height:380px;'>
            <div class='scn-line'></div>
            <img src='data:image/png;base64,{enc_img}'
                 style='width:100%;height:380px;object-fit:cover;opacity:.85;'>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Awaiting specimen ingestion for terminal initialization...")

# ─────────────────────────────────────────────────────────
#  INITIATE SEQUENCE
# ─────────────────────────────────────────────────────────
if img_bgr is not None:
    st.markdown("---")
    if st.button("🎆  INITIATE SUPREME ZENITH OVERDRIVE", use_container_width=True):

        # BIO-LOG
        ph_log = st.empty()
        logs = []
        def log(msg):
            logs.append(f"<span style='color:#4ade80;'>▶</span> {msg}")
            ph_log.markdown(
                f"""<div style='font-family:JetBrains Mono,monospace;background:#000;
                     padding:18px;border-radius:18px;border:1px solid #10b981;
                     color:#86efac;height:130px;overflow-y:auto;font-size:.85rem;'>
                {'<br>'.join(logs)}</div>""",
                unsafe_allow_html=True)
            time.sleep(0.15)

        log("Initializing Quantum Molecular Sync...")
        c_res = identify_crop_health(img_bgr)
        p_res = identify_plant_plantnet(img_bgr)

        plant_name = c_res.get('plant') or p_res.get('plant') or "Generic Specimen"
        pathogen   = c_res.get('disease', 'Healthy Spectrum')
        conf       = c_res.get('confidence', 0)
        sev        = c_res.get('severity_score', 0)
        rec_prob   = c_res.get('recovery_prob', 100)
        treatment  = c_res.get('treatment', 'Standard care recommended.')

        log(f"Plant Identified → {plant_name}")
        log(f"Pathogen Classified → {pathogen}")

        log("Calibrating Aer-127 Quantum Backend...")
        qc, ent = build_quantum_circuit(img_bgr)
        counts, _ = run_quantum(qc)
        risk_score, r_lvl = calculate_quantum_risk(counts, ent)

        log("Synthesizing Bio-Metrics...")
        ndvi   = compute_ndvi_score(img_bgr)
        wsi    = compute_water_stress_index(img_bgr)
        nitro  = estimate_nitrogen_content(img_bgr)
        npk    = estimate_npk_balance(img_bgr)
        bio_age = estimate_biological_age(img_bgr)
        carbon  = estimate_carbon_sequestration(ndvi, bio_age)
        rank    = calculate_global_rank(nitro['nitrogen_pct'], ndvi)
        vel     = calculate_degrade_velocity(risk_score)
        eff     = calculate_treatment_efficacy(sev, 20)
        msi     = calculate_molecular_stress_index(risk_score, wsi)

        log("Fetching procurement database...")
        links   = get_remedy_purchase_links(pathogen) if "healthy" not in pathogen.lower() else []

        log("Generating Pathogen Heatmap...")
        mask = generate_pathogen_mask(img_bgr)

        is_healthy = "healthy" in pathogen.lower()
        if is_healthy:
            st.markdown("""<script>
            document.getElementById('leaves_plantdoc').style.display='block';
            setTimeout(()=>document.getElementById('leaves_plantdoc').style.display='none',8000);
            </script>""", unsafe_allow_html=True)

        log("Dashboard construction complete ✓")
        ph_log.empty()

        # ─────────────────────────────────────────────────────────
        #  MAIN DASHBOARD
        # ─────────────────────────────────────────────────────────
        st.markdown("## 📊 Clinical Intelligence Dashboard")
        col_main, col_viz = st.columns([1.2, 0.8], gap="large")

        # ── LEFT PANEL ──
        with col_main:
            st.markdown("<div class='gcard'>", unsafe_allow_html=True)

            # PLANT NAME & STATUS
            st.markdown(f"<p class='plant-name'>{plant_name.upper()}</p>", unsafe_allow_html=True)
            dis_cls = "dis-healthy" if is_healthy else "dis-infected"
            st.markdown(f"<div class='disease-name {dis_cls}'>"
                        f"{'✅ HEALTHY SPECTRUM' if is_healthy else '⚠️ PATHOGEN: '+pathogen.upper()}"
                        f"</div>", unsafe_allow_html=True)
            
            # SEVERITY MATRIX
            st.markdown("<div class='mlabel' style='margin-top:20px;'>Pathogen Severity Matrix</div>", unsafe_allow_html=True)
            sev_bits = []
            levels = ["Low", "Stable", "Warning", "Critical", "Lethal"]
            for i in range(5):
                active = "active" if (sev/20) >= i else ""
                if i == 4 and sev > 80: active = "critical"
                sev_bits.append(f"<div class='sev-bit {active}' title='{levels[i]}'></div>")
            st.markdown(f"<div class='sev-matrix'>{''.join(sev_bits)}</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # HERO METRICS ROW
            m1, m2, m3, m4 = st.columns(4)
            metric_data = [
                ("AI Confidence", f"{conf:.0f}%", "#4ade80"),
                ("Pathogen Risk", f"{risk_score:.0f}%", "#f87171"),
                ("Recovery Prob", f"{rec_prob:.0f}%", "#60a5fa"),
                ("Stability Index", f"{100-sev:.0f}%", "#fbbf24"),
            ]
            for col, (label, val, color) in zip([m1,m2,m3,m4], metric_data):
                col.markdown(f"""<div class='mbox'>
                    <div class='mlabel'>{label}</div>
                    <div class='mval' style='color:{color};'>{val}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # BIO-STABILITY GAUGE
            gauge_color = get_health_gauge_color(sev)
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=100 - sev,
                title={'text': "Molecular Integrity Index", 'font': {'color': '#10b981', 'family': 'Michroma', 'size': 14}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#374151'},
                    'bar': {'color': gauge_color},
                    'bgcolor': 'rgba(0,0,0,0.3)',
                    'borderwidth': 2,
                    'steps': [
                        {'range': [0, 30],  'color': 'rgba(239,68,68,.2)'},
                        {'range': [30, 70], 'color': 'rgba(245,158,11,.2)'},
                        {'range': [70, 100],'color': 'rgba(16,185,129,.2)'}
                    ]
                }
            ))
            fig_g.update_layout(height=240, margin=dict(l=30,r=30,t=50,b=20),
                                 paper_bgcolor='rgba(0,0,0,0)', font_color='#9ca3af')
            st.plotly_chart(fig_g, use_container_width=True)

            st.markdown("---")

            # CLINICAL REMEDY BLOCK
            st.markdown("<b style='color:#10b981; font-family:Michroma; letter-spacing:3px;'>🧬 ACCURATE CLINICAL REMEDY PROTOCOL</b>", unsafe_allow_html=True)
            st.markdown(f"<div class='remedy-block'>{treatment}</div>", unsafe_allow_html=True)

            # PURCHASE LINKS
            if links:
                st.markdown("<br><b>🛒 Direct Procurement Database</b>", unsafe_allow_html=True)
                lc = st.columns(len(links))
                for i, lk in enumerate(links):
                    lc[i].markdown(
                        f"<a href='{lk['url']}' target='_blank' style='display:block;text-align:center;"
                        f"background:rgba(16,185,129,0.1);color:#4ade80;padding:16px;border-radius:24px;"
                        f"border:1px solid #10b981;text-decoration:none;font-weight:900;"
                        f"transition:0.3s;'>{lk['icon']} {lk['store']}</a>",
                        unsafe_allow_html=True)

            st.markdown("---")

            # ROI & LIFE EXPECTANCY
            roi = compute_treatment_roi(risk_score)
            
            # EXTENDED METRICS
            e1, e2 = st.columns(2)
            with e1:
                st.markdown(f"""<div class='mbox'>
                    <div class='mlabel'>Predicted Crop Savings</div>
                    <div class='mval' style='color:#34d399;font-size:2.5rem;'>${roi['crop_saved']:,.0f}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""<div class='mbox'>
                    <div class='mlabel'>ROI Yield Projection</div>
                    <div class='mval' style='color:#fbbf24;font-size:2.5rem;'>{roi['roi_pct']}%</div>
                </div>""", unsafe_allow_html=True)
            with e2:
                st.markdown(f"""<div class='mbox'>
                    <div class='mlabel'>Tissue Sustainability</div>
                    <div class='mval' style='color:#60a5fa;font-size:2.5rem;'>{eff}% Success</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""<div class='mbox'>
                    <div class='mlabel'>Life Expectancy (Days)</div>
                    <div class='mval' style='color:#ef4444;font-size:2.5rem;'>{roi['life_expectancy_days']}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(f"**Pathogen Spread Velocity:** `{vel}`")
            st.markdown(f"**NPK Saturation Matrix:** `N:{npk['n']}% | P:{npk['p']}% | K:{npk['k']}%`")
            st.markdown(f"**Photosynthetic Index (NDVI):** `{ndvi:.4f}`")
            st.markdown(f"**Treatment Strategy Verdict:** <span style='color:#10b981;font-weight:900;'>{roi['verdict']}</span>", unsafe_allow_html=True)

            st.markdown("---")
            # DNA STAMP
            wiki_q = plant_name.replace(' ', '_')
            st.markdown(f"📖 **[Advanced Ecological Knowledge Base → {plant_name}](https://en.wikipedia.org/wiki/{wiki_q})**")

            st.markdown("---")
            pdf_bytes = generate_pdf_report(plant_name, pathogen, conf, r_lvl,
                                             treatment, risk_score, 100-sev, 
                                             care_data={"roi": roi, "npk": npk}, 
                                             necrotic_ratio=sev,
                                             texture_data=compute_leaf_texture_score(img_bgr))
            st.download_button("📥 DOWNLOAD SUPREME ZENITH CLINICAL DOSSIER",
                               data=pdf_bytes,
                               file_name=f"PlantDoc_Zenith_Report.pdf",
                               mime="application/pdf",
                               use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ── RIGHT PANEL ──
        with col_viz:
            st.markdown("<div class='gcard' style='padding:36px;'>", unsafe_allow_html=True)
            viz_tabs = st.tabs(["🌀 3D Bio-Mesh", "🔥 Pathogen Map", "📈 7-Day Forecast", "⚛️ Gene Map"])

            with viz_tabs[0]:
                gray = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100))
                fig3d = go.Figure(data=[go.Surface(z=gray, colorscale='Viridis',
                                                    lighting=dict(roughness=.5, specular=.7))])
                fig3d.update_layout(height=420, margin=dict(l=0,r=0,t=0,b=0),
                                     paper_bgcolor='rgba(0,0,0,0)',
                                     scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False))
                st.plotly_chart(fig3d, use_container_width=True)
                st.caption("Topological leaf surface texture rendered in 3D.")

            with viz_tabs[1]:
                try:
                    overlay = cv2.addWeighted(
                        cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), 0.65,
                        cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB), 0.35, 0)
                    st.image(overlay, use_container_width=True,
                             caption="🔴 Highlighted zones = Pathogen saturation areas")
                except:
                    st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)

            with viz_tabs[2]:
                forecast = generate_growth_forecast(ndvi)
                df_fc = pd.DataFrame({"Day": [f"D+{i}" for i in range(7)], "NDVI Index": forecast})
                fig_fc = px.area(df_fc, x="Day", y="NDVI Index",
                                  color_discrete_sequence=["#4ade80"])
                fig_fc.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)',
                                      font_color='#9ca3af',
                                      xaxis=dict(gridcolor='#1f2937'),
                                      yaxis=dict(gridcolor='#1f2937'))
                st.plotly_chart(fig_fc, use_container_width=True)
                st.caption("Projected photosynthetic NDVI accumulation over 7 days.")

            with viz_tabs[3]:
                dna = "".join(["ATCG"[hash(plant_name + str(j)) % 4] for j in range(240)])
                if not is_healthy:
                    dna = dna.replace("T", "<span style='color:#f87171;font-weight:900;'>!</span>")
                st.markdown(
                    f"<div style='font-family:JetBrains Mono;font-size:.8rem;color:#10b981;"
                    f"word-break:break-all;background:#000;padding:20px;border-radius:14px;"
                    f"border:1px solid #064e3b;line-height:1.6;'>{dna}</div>",
                    unsafe_allow_html=True)
                st.caption("Simulated genomic strand with pathogen insertion markers.")

            st.markdown("</div>", unsafe_allow_html=True)

        # ── CORE FEATURES OVERVIEW ──
        st.markdown("---")
        st.markdown("## 🏆 System Strengths & Feature Matrix")
        frows = st.columns(3)
        features = [
            ("01", "Quantum-AI Fusion Core", "Hybrid 127-qubit Qiskit + PlantNet/Kindwise deep-learning pipeline for clinical-grade consensus.", "#4ade80"),
            ("02", "Molecular Remedy Engine", "Pathogen-specific treatment protocols with resistance-indexed procurement links.", "#60a5fa"),
            ("03", "Photosynthetic Analytics", "Real-time NDVI, WSI, and Carbon Sequestration from raw pixel-domain multispectral analysis.", "#a78bfa"),
            ("04", "Economic Bio-ROI", "Farm yield impact estimation, treatment efficacy forecasting, and financial recovery probability.", "#fbbf24"),
            ("05", "Live Environmental Sync", "Sunrise-Sunset API telemetry for real photoperiod data influencing metabolic predictions.", "#34d399"),
            ("06", "Zenith Oracle v13", "Multi-weight NLP engine for clinical botanical consultation on any growth or disease topic.", "#f87171"),
        ]
        for i, (rank, title, desc, color) in enumerate(features):
            with frows[i % 3]:
                st.markdown(f"""<div class='feat-item'>
                    <span style='color:{color};font-family:JetBrains Mono;font-weight:900;'>#{rank}</span>
                    <b style='color:#fff; display:block; margin-top:4px;'>{title}</b>
                    <small style='color:#6b7280;'>{desc}</small>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  ZENITH ORACLE
# ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<h2 style='font-family:Syne;font-size:4rem;color:#4ade80;text-align:center;'>🤖 Zenith Oracle</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#6b7280;'>Ask about plant health, productivity, irrigation, soil, or specific diseases</p>", unsafe_allow_html=True)

oracle_q = st.text_input("", placeholder="How to enhance productivity? | Signs of late blight? | Irrigation best practices?", label_visibility="collapsed")
if oracle_q:
    ans = get_disease_info(oracle_q)
    sev_colors = {"low":"#10b981","info":"#60a5fa","medium":"#fbbf24","high":"#f97316","critical":"#ef4444","unknown":"#6b7280"}
    sev_c = sev_colors.get(ans.get('severity','unknown'), '#6b7280')
    st.markdown(f"""
    <div style='background:rgba(10,10,10,.95);border:3px solid #4ade80;padding:50px;border-radius:40px;
                box-shadow:0 0 100px rgba(34,197,94,.25); margin-top:20px;'>
        <h3 style='color:#4ade80;font-family:Syne;margin-top:0;'>Oracle Response</h3>
        <p style='font-size:1.35rem;color:#d1fae5;line-height:1.75;'>{ans['tips']}</p>
        <span style='background:{sev_c};color:#000;padding:10px 30px;border-radius:20px;
                     font-weight:900;font-family:Michroma;font-size:1rem;'>
            SEVERITY CLASS: {ans.get("severity","unknown").upper()}
        </span>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""<div style='text-align:center;color:#374151;padding:40px;
             border-top:1px solid #1f2937;font-family:Space Grotesk;'>
    <b style='color:#4ade80;'>PlantDoc</b> — Zenith Bioscience Terminal<br>
    <small>© 2026 Sovereign Agritech Collective</small>
</div>""", unsafe_allow_html=True)
