import re
import os

target_file = r"c:\Users\Admin\OneDrive\Desktop\quantum-computing\quantum-computing-main\QUANNT\quantum\app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the giant CSS block
new_css = '''<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

    /* ── RESET & BASE ── */
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif !important;
    }

    /* ── BACKGROUND: Organic Wood ── */
    .stApp, .main {
        background-color: #2E1C15 !important;
        background-image: radial-gradient(circle at 50% 0%, #4E342E 0%, #2E1C15 80%);
    }

    /* ── MAIN HEADER ── */
    .main-header {
        font-family: 'Nunito', sans-serif !important;
        font-size: clamp(3rem, 6vw, 5rem) !important;
        font-weight: 900 !important;
        color: #81C784 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        border-left: 8px solid #4CAF50;
        padding-left: 1rem;
        margin-bottom: 0 !important;
    }

    /* ── METRIC CARD ── */
    .metric-card {
        background: #3E2723;
        border: 2px solid #5D4037;
        border-radius: 16px !important;
        padding: 22px;
        text-align: center;
        position: relative;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(76, 175, 80, 0.2);
        border-color: #4CAF50;
    }

    /* ── STATUS BADGE ── */
    .status-badge {
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 700;
        background: #4CAF50;
        color: #fff;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #3E2723 !important;
        border-right: 2px solid #5D4037 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #A5D6A7 !important;
        font-weight: 800;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        background: #4CAF50 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 10px rgba(76, 175, 80, 0.3) !important;
        transition: transform 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #43A047 !important;
        transform: translateY(-3px) !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 2px solid #5D4037 !important;
        gap: 8px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: #4E342E !important;
        border-radius: 12px 12px 0 0 !important;
        color: #A1887F !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
    }
    .stTabs [aria-selected="true"] {
        background: #4CAF50 !important;
        color: #fff !important;
        border-color: #4CAF50 !important;
    }

    /* ── EXPANDER ── */
    [data-testid="stExpander"] {
        border: 2px solid #5D4037 !important;
        border-radius: 12px !important;
        background: #3E2723 !important;
    }

    /* ── METRICS ── */
    [data-testid="stMetric"] {
        background: #3E2723 !important;
        border: 2px solid #5D4037 !important;
        border-radius: 16px !important;
        padding: 16px !important;
    }
    [data-testid="stMetricValue"] {
        color: #81C784 !important;
        font-weight: 900 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #A1887F !important;
        font-weight: 700 !important;
    }
    
    .quantum-glow {
        color: #4CAF50 !important;
        text-shadow: 0 0 10px rgba(76, 175, 80, 0.5) !important;
    }

</style>'''

content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)
content = content.replace("PlantPulse // GROT", "I AM GROOT")
content = content.replace("BOTANICAL DIAGNOSTICS — HYBRID ENTANGLEMENT VERIFICATION SYSTEM", "I am Groot. (Hybrid Botanical Diagnostics)")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)
