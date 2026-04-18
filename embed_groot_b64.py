import base64
import re

image_path = r"C:\Users\Admin\.gemini\antigravity\brain\7dc34414-9cef-421f-ad35-21e99bf02ff3\media__1776539390874.jpg"
app_path = r"c:\Users\Admin\OneDrive\Desktop\quantum-computing\quantum-computing-main\QUANNT\quantum\app.py"

with open(image_path, "rb") as f:
    encoded_string = base64.b64encode(f.read()).decode("utf-8")

data_url = f"data:image/jpeg;base64,{encoded_string}"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the tenor url or any img src in the sidebar with the base64 String
sidebar_html = f"""# Sidebar
with st.sidebar:
    st.markdown("<img src='{data_url}' class='groot-sidebar-img'>", unsafe_allow_html=True)"""

content = re.sub(r'# Sidebar\nwith st\.sidebar:\n    st\.markdown\("<img src=[^>]+>", unsafe_allow_html=True\)', sidebar_html, content)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)
