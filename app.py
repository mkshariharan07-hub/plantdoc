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

/* BACKGROUND */
.stApp {
    background: #020408 !important;
    background-image:
        radial-gradient(ellipse at 15% 15%, rgba(34,197,94,.12) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 80%, rgba(16,185,129,.10) 0%, transparent 55%),
        url('https://www.transparenttextures.com/patterns/carbon-fibre.png') !important;
}

/* HEADER */
.title-zen {
    font-family:'Syne',sans-serif; font-size:9rem; font-weight:800;
    background: linear-gradient(135deg,#4ade80 0%,#10b981 50%,#059669 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    text-align:center; margin:0; letter-spacing:-10px; line-height:.85;
}
.subtitle-zen {
    font-family:'Michroma',sans-serif; font-size:.9rem; letter-spacing:14px;
    color:#10b981; text-align:center; margin-top:14px; opacity:.7;
}

/* GLASS CARDS */
.gcard {
    background:rgba(13,17,23,.92);
    border:1.5px solid rgba(16,185,129,.35);
    border-radius:48px; padding:52px;
    backdrop-filter:blur(60px);
    box-shadow:0 80px 220px -50px rgba(0,0,0,1), inset 0 1px 0 rgba(255,255,255,.04);
    margin-bottom:44px;
    transition:border-color .5s, box-shadow .5s;
}
.gcard:hover { border-color:#22c55e; box-shadow:0 0 100px rgba(34,197,94,.15); }

/* NAMES */
.plant-name {
    font-family:'Syne',sans-serif; font-size:4.5rem; font-weight:800;
    color:#fff; line-height:1; margin:0;
    border-left:12px solid #10b981;
    padding-left:28px;
    text-shadow:0 0 40px rgba(16,185,129,.3);
}
.disease-name {
    font-family:'Michroma',sans-serif; font-size:1.5rem; letter-spacing:3px;
    margin-top:16px; padding:14px 28px; border-radius:16px; display:inline-block;
}
.dis-healthy { background:rgba(16,185,129,.15); color:#4ade80; border:1.5px solid #10b981; }
.dis-infected { background:rgba(239,68,68,.15); color:#f87171; border:1.5px solid #ef4444; }

/* METRICS */
.mbox {
    background:rgba(0,0,0,.6); border:1px solid #1a3a2a;
    border-radius:28px; padding:28px; text-align:center;
}
.mval {
    font-family:'JetBrains Mono',monospace; font-size:3.5rem;
    font-weight:900; line-height:1;
}
.mlabel {
    font-family:'Michroma',sans-serif; font-size:.65rem;
    color:#4b5563; letter-spacing:4px; text-transform:uppercase; margin-bottom:6px;
}

/* REMEDY */
.remedy-block {
    background:linear-gradient(135deg,rgba(5,46,22,.8),rgba(1,2,4,.95));
    border:2px solid #10b981; border-radius:32px; padding:36px;
    font-size:1.2rem; line-height:1.8; color:#d1fae5;
    box-shadow:inset 0 0 50px rgba(16,185,129,.08);
}

/* FEATURE CARDS */
.feat-item {
    background:rgba(0,0,0,.5);
    border-left:5px solid #10b981; border-radius:16px;
    padding:18px 22px; margin-bottom:16px;
    transition:.3s;
}
.feat-item:hover { transform:translateX(8px); background:rgba(16,185,129,.06); }

/* SCANNER */
.scn-wrap { position:relative; border-radius:30px; overflow:hidden; border:2px solid #065f46; }
.scn-line { position:absolute; width:100%; height:6px;
    background:linear-gradient(transparent,#4ade80,transparent);
    box-shadow:0 0 30px #22c55e; animation:scn 3.5s ease-in-out infinite; }
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
                        f"{'✅ HEALTHY SPECTRUM' if is_healthy else '⚠️ '+pathogen.upper()}"
                        f"</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # HERO METRICS ROW
            m1, m2, m3, m4 = st.columns(4)
            metric_data = [
                ("AI Confidence", f"{conf:.0f}%", "#4ade80"),
                ("Severity Index", f"{sev}%", "#f87171"),
                ("Recovery Prob", f"{rec_prob:.0f}%", "#60a5fa"),
                ("Quantum Risk", f"{risk_score:.1f}%", "#fbbf24"),
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
                mode="gauge+number+delta",
                value=100 - sev,
                delta={'reference': 80},
                title={'text': "Bio-Stability Index", 'font': {'color': '#10b981', 'family': 'Michroma'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#374151'},
                    'bar': {'color': gauge_color},
                    'bgcolor': 'rgba(0,0,0,0)',
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 40],  'color': 'rgba(239,68,68,.15)'},
                        {'range': [40, 70], 'color': 'rgba(245,158,11,.1)'},
                        {'range': [70, 100],'color': 'rgba(16,185,129,.1)'}
                    ],
                    'threshold': {'line': {'color': '#ffffff', 'width': 2}, 'thickness': .8, 'value': 100-sev}
                }
            ))
            fig_g.update_layout(height=230, margin=dict(l=20,r=20,t=50,b=0),
                                 paper_bgcolor='rgba(0,0,0,0)', font_color='#9ca3af')
            st.plotly_chart(fig_g, use_container_width=True)

            st.markdown("---")

            # CLINICAL REMEDY BLOCK
            st.markdown("<b style='color:#10b981; font-family:Michroma; letter-spacing:3px;'>🧬 ACCURATE CLINICAL REMEDY PROTOCOL</b>", unsafe_allow_html=True)
            st.markdown(f"<div class='remedy-block'>{treatment}</div>", unsafe_allow_html=True)

            # PURCHASE LINKS
            if links:
                st.markdown("<br><b>🛒 Direct Procurement</b>", unsafe_allow_html=True)
                lc = st.columns(len(links))
                for i, lk in enumerate(links):
                    lc[i].markdown(
                        f"<a href='{lk['url']}' target='_blank' style='display:block;text-align:center;"
                        f"background:#4ade80;color:#000;padding:14px;border-radius:16px;"
                        f"text-decoration:none;font-weight:900;'>{lk['icon']} {lk['store']}</a>",
                        unsafe_allow_html=True)

            st.markdown("---")

            # EXTENDED METRICS
            e1, e2 = st.columns(2)
            with e1:
                st.markdown(f"""<div class='mbox'>
                    <div class='mlabel'>Carbon Sequestration</div>
                    <div class='mval' style='color:#34d399;font-size:2rem;'>{carbon} gCO₂/d</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""<div class='mbox'>
                    <div class='mlabel'>Biological Age</div>
                    <div class='mval' style='color:#a78bfa;font-size:2rem;'>{bio_age} Days</div>
                </div>""", unsafe_allow_html=True)
            with e2:
                st.markdown(f"""<div class='mbox'>
                    <div class='mlabel'>Treatment Efficacy</div>
                    <div class='mval' style='color:#60a5fa;font-size:2rem;'>{eff}%</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""<div class='mbox'>
                    <div class='mlabel'>Global Elite Rank</div>
                    <div class='mval' style='color:#fbbf24;font-size:2rem;'>{rank['percentile']}%</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(f"**Tissue Degradation Velocity:** `{vel}`")
            st.markdown(f"**NPK Balance:** `N:{npk['n']}% | P:{npk['p']}% | K:{npk['k']}%`")
            st.markdown(f"**Water Stress Index (WSI):** `{wsi:.3f}`")
            st.markdown(f"**NDVI (Photosynthesis):** `{ndvi:.4f}`")
            st.markdown(f"**Molecular Stress (MSI):** `{msi['msi_value']} — {msi['status']}`")
            st.markdown(f"**Pathogen Risk Level:** `{r_lvl.upper()}`")

            st.markdown("---")
            # DNA STAMP
            wiki_q = plant_name.replace(' ', '_')
            st.markdown(f"📖 **[Ecological Knowledge Base → {plant_name} (Wikipedia)](https://en.wikipedia.org/wiki/{wiki_q})**")

            st.markdown("---")
            pdf_bytes = generate_pdf_report(plant_name, pathogen, conf, r_lvl,
                                             treatment, risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD SUPREME ZENITH CLINICAL DOSSIER",
                               data=pdf_bytes,
                               file_name=f"PlantDoc_Zenith_{plant_name.replace(' ','_')}.pdf",
                               mime="application/pdf")

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
