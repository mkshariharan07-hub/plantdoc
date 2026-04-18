import base64
import re
import os

image_path = r"C:\Users\Admin\.gemini\antigravity\brain\7dc34414-9cef-421f-ad35-21e99bf02ff3\media__1776539390874.jpg"
plantdoc_app_path = r"c:\Users\Admin\Downloads\GitHub\plantdoc\app.py"

with open(image_path, "rb") as f:
    encoded_string = base64.b64encode(f.read()).decode("utf-8")

data_url = f"data:image/jpeg;base64,{encoded_string}"

with open(plantdoc_app_path, "r", encoding="utf-8") as f:
    content = f.read()

new_css = '''<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; }

    .stApp, .main {
        background-color: #1c2b18 !important;
        background-image: radial-gradient(circle at 50% 30%, rgba(206, 230, 94, 0.15) 0%, transparent 60%), linear-gradient(180deg, #1f361c 0%, #171d15 100%) !important;
    }

    .main-header {
        font-family: 'Nunito', sans-serif !important; font-size: clamp(3rem, 6vw, 5rem) !important; font-weight: 900 !important; color: #b4df41 !important;
        text-shadow: 0px 4px 12px rgba(180, 223, 65, 0.4), 2px 2px 4px rgba(0,0,0,0.8); border-left: 8px solid #b4df41; padding-left: 1rem; margin-bottom: 0 !important;
    }

    .metric-card, .glass-panel, .action-step, .care-row, .pipeline-step, .history-card, .purchase-button {
        background: rgba(46, 31, 23, 0.85) !important; border: 2px solid #5d4037 !important; border-radius: 20px !important; padding: 22px; text-align: center;
        position: relative; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); box-shadow: 0 8px 16px rgba(0,0,0,0.4) !important; backdrop-filter: blur(5px);
        color: #b4df41 !important;
    }
    .metric-card:hover, .glass-panel:hover, .action-step:hover, .pipeline-step:hover {
        transform: translateY(-8px) scale(1.02); box-shadow: 0 15px 30px rgba(180, 223, 65, 0.3) !important; border-color: #b4df41 !important;
    }
    .metric-card h2 { color: #b4df41 !important; font-family: 'Nunito', sans-serif !important; font-size: 2.5rem !important; }
    
    .hero-title {
        font-family: 'Nunito', sans-serif !important; font-size: 5rem !important; color: #b4df41 !important; background: none !important;
        -webkit-background-clip: unset !important; -webkit-text-fill-color: currentcolor !important;
        text-shadow: 2px 2px 0px #000, 4px 4px 0px rgba(180, 223, 65, 0.3) !important; letter-spacing: 0.05em; text-transform: uppercase;
    }
    .quantum-badge {
        background: linear-gradient(135deg, #7cb342, #558b2f) !important; color: #fff !important; border-radius: 50px !important; border: 2px solid #558b2f !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #8bc34a, #689f38) !important; color: #111 !important; border: 2px solid #aed581 !important;
        border-radius: 15px !important; font-weight: 900 !important; font-size: 1.1rem !important; box-shadow: 0 6px 15px rgba(104, 159, 56, 0.4) !important;
        transition: all 0.3s ease !important; text-transform: uppercase;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #9ccc65, #7cb342) !important; transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 10px 20px rgba(104, 159, 56, 0.6) !important; border-color: #dcedc8 !important;
    }

    [data-testid="stSidebar"] { background: #2e1c15 !important; border-right: 3px solid #5d4037 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #c5e1a5 !important; font-weight: 800; }

    .health-bar-container { border-radius: 50px !important; border: 2px solid #5d4037; background: rgba(0,0,0,0.5); }
    .health-bar-fill { background: linear-gradient(90deg, #7cb342, #b4df41) !important; border-radius: 50px !important; }

    #MainMenu, footer { visibility: hidden; }

    .stTextInput>div>div>input, [data-testid="stExpander"] {
        border-radius: 12px !important; border: 2px solid #5d4037 !important; background: rgba(62, 39, 35, 0.8) !important; color: #fff !important;
    }
    .stTextInput>div>div>input:focus, [data-testid="stExpander"]:hover { border-color: #b4df41 !important; }

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

# Find the sidebar area in plantdoc/app.py 
# It looks like:
# with st.sidebar:
#     st.image("https://... or st.image(r"C:...
sidebar_pattern = r'# SIDEBAR\n# ===============================\nwith st\.sidebar:\n    st\.image\([^)]+\)'

sidebar_html = f"""# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown("<img src='{data_url}' class='groot-sidebar-img'>", unsafe_allow_html=True)"""

content = re.sub(sidebar_pattern, sidebar_html, content)

content = content.replace("GROT ENGINE // 3D QUANTUM", "I AM GROOT // BOTANICAL ASSISTANT")

with open(plantdoc_app_path, "w", encoding="utf-8") as f:
    f.write(content)
