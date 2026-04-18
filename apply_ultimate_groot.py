import re
import os

target_file = r"c:\Users\Admin\OneDrive\Desktop\quantum-computing\quantum-computing-main\QUANNT\quantum\app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

new_css = '''<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

    /* ── RESET & BASE ── */
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif !important;
    }

    /* ── BACKGROUND: Magic Forest ── */
    .stApp, .main {
        background-color: #1c2b18 !important; /* Deep forest green */
        background-image: 
            radial-gradient(circle at 50% 30%, rgba(206, 230, 94, 0.15) 0%, transparent 60%),
            linear-gradient(180deg, #1f361c 0%, #171d15 100%) !important;
    }

    /* ── MAIN HEADER ── */
    .main-header {
        font-family: 'Nunito', sans-serif !important;
        font-size: clamp(3rem, 6vw, 5rem) !important;
        font-weight: 900 !important;
        color: #b4df41 !important; /* Vibrant bright leaf green */
        text-shadow: 0px 4px 12px rgba(180, 223, 65, 0.4), 2px 2px 4px rgba(0,0,0,0.8);
        border-left: 8px solid #b4df41;
        padding-left: 1rem;
        margin-bottom: 0 !important;
    }

    /* ── METRIC CARD ── */
    .metric-card {
        background: rgba(46, 31, 23, 0.85); /* Deep bark brown */
        border: 2px solid #5d4037;
        border-radius: 20px !important;
        padding: 22px;
        text-align: center;
        position: relative;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        backdrop-filter: blur(5px);
    }
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 30px rgba(180, 223, 65, 0.3);
        border-color: #b4df41;
    }

    /* ── STATUS BADGE ── */
    .status-badge {
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #7cb342, #558b2f);
        color: #fff;
        box-shadow: 0 2px 8px rgba(124, 179, 66, 0.5);
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #2e1c15 !important;
        border-right: 3px solid #5d4037 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #c5e1a5 !important;
        font-weight: 800;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        background: linear-gradient(135deg, #8bc34a, #689f38) !important;
        color: #111 !important;
        border: 2px solid #aed581 !important;
        border-radius: 15px !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 6px 15px rgba(104, 159, 56, 0.4) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #9ccc65, #7cb342) !important;
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 10px 20px rgba(104, 159, 56, 0.6) !important;
        border-color: #dcedc8 !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 2px solid #5d4037 !important; }
    .stTabs [data-baseweb="tab"] { background: #3e2723 !important; border-radius: 12px 12px 0 0 !important; color: #a1887f !important; font-weight: 700 !important; }
    .stTabs [aria-selected="true"] { background: #558b2f !important; color: #fff !important; border-color: #7cb342 !important; }

    /* ── EXPANDER ── */
    [data-testid="stExpander"] { border: 2px solid #5d4037 !important; border-radius: 12px !important; background: rgba(62, 39, 35, 0.8) !important; }

    /* ── METRICS ── */
    [data-testid="stMetric"] { background: #3e2723 !important; border: 2px solid #5d4037 !important; border-radius: 16px !important; padding: 16px !important; }
    [data-testid="stMetricValue"] { color: #b4df41 !important; font-weight: 900 !important; }
    [data-testid="stMetricLabel"] { color: #a1887f !important; font-weight: 700 !important; }
    
    .quantum-glow { color: #b4df41 !important; text-shadow: 0 0 12px rgba(180, 223, 65, 0.6) !important; }

    /* ── CSS FALLING LEAVES ANIMATION ── */
    @keyframes fallAndSway {
        0% { transform: translateY(-10vh) rotate(0deg) translateX(0px); opacity: 0; }
        10% { opacity: 1; }
        50% { transform: translateY(50vh) rotate(180deg) translateX(30px); }
        90% { opacity: 1; }
        100% { transform: translateY(110vh) rotate(360deg) translateX(-30px); opacity: 0; }
    }
    .magical-leaf {
        position: fixed; top: -10vh; z-index: 999; pointer-events: none;
        font-size: 28px; filter: drop-shadow(0 0 8px rgba(180, 223, 65, 0.6));
        animation: fallAndSway linear infinite;
    }
    .magical-leaf:nth-child(1) { left: 5%; animation-duration: 12s; animation-delay: 0s; font-size: 20px; }
    .magical-leaf:nth-child(2) { left: 25%; animation-duration: 15s; animation-delay: 4s; font-size: 30px;}
    .magical-leaf:nth-child(3) { left: 50%; animation-duration: 10s; animation-delay: 2s; font-size: 25px;}
    .magical-leaf:nth-child(4) { left: 75%; animation-duration: 18s; animation-delay: 1s; font-size: 22px;}
    .magical-leaf:nth-child(5) { left: 90%; animation-duration: 14s; animation-delay: 5s; font-size: 28px;}
    .magical-leaf:nth-child(6) { left: 15%; animation-duration: 13s; animation-delay: 7s; font-size: 24px;}
    .magical-leaf:nth-child(7) { left: 65%; animation-duration: 16s; animation-delay: 3s; font-size: 26px;}

    /* Dancing Groot Sidebar Image Bounce */
    @keyframes grootBounce {
        0%, 100% { transform: scale(1) translateY(0); filter: drop-shadow(0 0 10px rgba(124, 179, 66, 0.5)); }
        50% { transform: scale(1.02) translateY(-4px); filter: drop-shadow(0 10px 20px rgba(180, 223, 65, 0.8)); }
    }
    .groot-sidebar-img {
        border: 4px solid #7cb342; border-radius: 16px; margin-bottom: 20px; width: 100%;
        animation: grootBounce 3s ease-in-out infinite;
    }
</style>
<div class="magical-leaf">🌿</div>
<div class="magical-leaf">🍂</div>
<div class="magical-leaf">🍃</div>
<div class="magical-leaf">🌱</div>
<div class="magical-leaf">🌿</div>
<div class="magical-leaf">🍃</div>
<div class="magical-leaf">🍀</div>
'''

content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)

# Re-inject the animated GIF since they specifically asked for ANIMATION of THIS character
sidebar_html = """# Sidebar
with st.sidebar:
    st.markdown("<img src='https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif' class='groot-sidebar-img'>", unsafe_allow_html=True)"""

content = re.sub(r'# Sidebar\nwith st\.sidebar:\n    st\.image\(r"[^"]+", use_container_width=True\)', sidebar_html, content)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)
