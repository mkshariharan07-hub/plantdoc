import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the giant CSS block
new_css = '''<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;700&display=swap');

    html, body, [class*="css"] { font-family: 'Space Mono', monospace !important; }

    .main, .stApp { background: #0D0D0D !important; color: #F0EDE8; }
    .block-container { background: transparent !important; padding-top: 1rem !important; }

    /* GROT BRUTALIST OVERRIDES FOR CUSTOM COMPONENTS */
    .metric-card, .glass-panel, .action-step, .care-row, .pipeline-step, .history-card, .purchase-button {
        background: #111 !important;
        border: 2px solid #FF4500 !important;
        border-radius: 0px !important;
        padding: 1.5rem;
        box-shadow: 4px 4px 0px #FF4500 !important;
        backdrop-filter: none !important;
        transition: transform 0.1s;
        color: #F0EDE8 !important;
        margin-bottom: 1rem;
    }
    .metric-card:hover, .glass-panel:hover, .action-step:hover, .pipeline-step:hover {
        transform: translate(-4px, -4px);
        box-shadow: 8px 8px 0px #FF4500 !important;
    }
    .metric-card h2 { color: #FF4500 !important; font-family: 'Bebas Neue', sans-serif !important; font-size: 2.5rem !important; }
    
    .hero-title {
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 5rem !important;
        color: #FF4500 !important;
        background: none !important;
        -webkit-background-clip: unset !important;
        -webkit-text-fill-color: currentcolor !important;
        text-shadow: 4px 4px 0px #000, 6px 6px 0px rgba(255,69,0,0.3) !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .quantum-badge {
        background: #FF4500 !important; color: #000 !important;
        border-radius: 0 !important; border: 2px solid #FF4500 !important;
        font-family: 'IBM Plex Mono', monospace !important; font-weight: bold;
    }

    .stButton>button {
        background: #FF4500 !important; color: #000 !important;
        border-radius: 0 !important; border: 2px solid #FF4500 !important;
        box-shadow: 4px 4px 0px #000 !important; font-family: 'IBM Plex Mono'; font-weight: bold;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background: #000 !important; color: #FF4500 !important;
        transform: translate(-3px, -3px) !important; box-shadow: 7px 7px 0px #FF4500 !important;
    }

    .health-bar-container { border-radius: 0 !important; border: 2px solid #FF4500; background: #222; }
    .health-bar-fill { background: #FF4500 !important; border-radius: 0 !important; box-shadow: none !important; }

    /* Hide Streamlit elements */
    #MainMenu, footer { visibility: hidden; }

    .stTextInput>div>div>input, [data-testid="stExpander"] {
        border-radius: 0 !important; border: 2px solid #333 !important; background: #111 !important; color: #fff !important;
    }
    .stTextInput>div>div>input:focus, [data-testid="stExpander"]:hover { border-color: #FF4500 !important; }

</style>'''

content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)

# Also replace the sidebar image
content = content.replace('st.image("https://img.icons8.com/color/144/leaf.png", width=90)', 
                          'st.image("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1400&auto=format&fit=crop", use_container_width=True)')

# Update text references
content = content.replace('PlantPulse Engine', 'GROT ENGINE // 3D QUANTUM')
content = content.replace('color: #a855f7', 'color: #FF4500')

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
