import streamlit as st
import yt_dlp
import re
import time

st.set_page_config(page_title="TDwnuXTw ®", layout="wide")

st.markdown("""
<style>
/* Reset and basic layout */
.stApp { background-color: #1e1e2f; color: #fff; }
h1 { text-align: center; color: #00d2ff; }

/* Custom Row Styles */
.row-container {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

/* Colors by Platform */
.bg-youtube { background-color: #5a0000 !important; border: 1px solid #ff0000; }
.bg-facebook { background-color: #002244 !important; border: 1px solid #1877F2; }
.bg-twitter { background-color: #111 !important; border: 1px solid #555; }
.bg-tiktok { background: linear-gradient(135deg, #111, #222) !important; border: 1px solid #00f2fe; } /* Simplification */
.bg-instagram { background: linear-gradient(135deg, #400040, #401000) !important; border: 1px solid #fd1d1d; }
.bg-other { background-color: #333 !important; border: 1px solid #555; }

/* Boxes */
.info-box, .av-box, .qual-box {
    padding: 10px;
    border-radius: 8px;
    height: 60px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
}

.info-box { flex: 3; }
.av-box { flex: 1; text-align: center; }
.qual-box { flex: 1; text-align: center; }
.dl-btn-col { flex: 0.5; }

.truncate {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.url-text { font-size: 0.8em; color: #00d2ff; }
.title-text { font-weight: bold; font-size: 1em; }

/* Streamlit specific overrides to make columns look like a row */
[data-testid="column"] {
    background: transparent !important;
}

.dl-btn {
    background-color: #28a745 !important;
    color: white !important;
    height: 60px !important;
    width: 100% !important;
    border-radius: 8px !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

st.title("TDwnuXTw ®")
st.markdown("### | Adquisidor de videos multiplataforma")

if 'links_data' not in st.session_state:
    st.session_state.links_data = []

def get_platform(url):
    url = url.lower()
    if 'youtube.com' in url or 'youtu.be' in url: return 'youtube'
    if 'facebook.com' in url or 'fb.watch' in url: return 'facebook'
    if 'twitter.com' in url or 'x.com' in url: return 'twitter'
    if 'tiktok.com' in url: return 'tiktok'
    if 'instagram.com' in url: return 'instagram'
    return 'other'

def fetch_meta(url):
    # Dummy fetch for fast UI testing
    return {
        "title": "Video Title Example",
        "thumbnail": "https://via.placeholder.com/120x60",
        "platform": get_platform(url)
    }

url_input = st.text_input("🔗 Pega los enlaces aquí:", key="url_input_widget")
if url_input:
    # Add to state if not exists
    if not any(d['url'] == url_input for d in st.session_state.links_data):
        meta = fetch_meta(url_input)
        st.session_state.links_data.append({
            'url': url_input,
            'title': meta['title'],
            'thumbnail': meta['thumbnail'],
            'platform': meta['platform'],
            'format': 'Video',
            'quality': '720p'
        })

# Render Rows
for idx, data in enumerate(st.session_state.links_data):
    plat = data['platform']
    bg_class = f"bg-{plat}"
    
    col_thumb, col_info, col_av, col_qual, col_dl = st.columns([1, 4, 1.5, 2, 1])
    
    with col_thumb:
        st.image(data['thumbnail'], use_container_width=True)
        
    with col_info:
        st.markdown(f"""
        <div class="info-box {bg_class}">
            <div class="title-text truncate">▶️ {data['title']}</div>
            <div class="url-text truncate">{data['url']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_av:
        st.markdown(f"""<div class="av-box {bg_class}" style="padding:0;">""", unsafe_allow_html=True)
        fmt = st.radio("Fmt", ["Video", "Audio"], horizontal=True, label_visibility="collapsed", key=f"fmt_{idx}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_qual:
        st.markdown(f"""<div class="qual-box {bg_class}" style="padding:0;">""", unsafe_allow_html=True)
        if fmt == "Video":
            qual = st.selectbox("Cal", ["1080p", "720p", "480p", "360p"], label_visibility="collapsed", key=f"q_{idx}")
        else:
            qual = st.selectbox("Cal", ["320 Kbps", "256 Kbps", "128 Kbps"], label_visibility="collapsed", key=f"q_{idx}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_dl:
        if st.button("📥", key=f"dl_{idx}", use_container_width=True):
            st.toast(f"Descargando {data['url']}")
            
    with st.expander("Logs"):
        st.write("Nivel 1...")
    
    st.markdown("---")
