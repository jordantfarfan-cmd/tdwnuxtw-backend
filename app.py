import streamlit as st
import yt_dlp
import os
import time
import random
import requests
import re
import urllib.parse
import threading

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="TDwnuXTw ® | Adquisidor de videos multiplataforma",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LIMPIEZA AUTOMÁTICA ---
def cleanup_old_downloads():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    else:
        # Borrar archivos con más de 1 hora de antigüedad
        now = time.time()
        for filename in os.listdir('downloads'):
            filepath = os.path.join('downloads', filename)
            if os.path.isfile(filepath):
                # Si el archivo tiene más de 3600 segundos (1 hora)
                if os.stat(filepath).st_mtime < now - 3600:
                    try:
                        os.remove(filepath)
                    except:
                        pass

cleanup_old_downloads()

# --- ESTILO PREMIUM (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1c1a29 0%, #2b2b40 100%);
        color: #ffffff;
    }
    
    /* Ocultar barra de Streamlit y pie de página */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1 {
        text-align: center;
        color: #00d2ff;
        font-weight: 800;
        margin-bottom: 0;
    }
    h3 {
        text-align: center;
        color: #ffffff;
        font-weight: 400;
        margin-top: 0;
        margin-bottom: 30px;
    }
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00d2ff !important;
    }
    
    /* Global Radio and Selectbox Styling */
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px;
        padding: 5px 10px;
        margin-bottom: 5px;
        transition: all 0.3s;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
        background-color: rgba(0, 210, 255, 0.2) !important;
        border-color: #00d2ff !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Clases de plataformas para la URL */
    .bg-youtube { background-color: #5a0a0a !important; border: 1px solid #ff0000; border-radius:8px; padding:6px 10px; display:inline-block; overflow:hidden; width: fit-content; max-width: 100%;}
    .bg-facebook { background-color: #0b1c3c !important; border: 1px solid #1877F2; border-radius:8px; padding:6px 10px; display:inline-block; overflow:hidden; width: fit-content; max-width: 100%;}
    .bg-tiktok { background: linear-gradient(135deg, #000, #111) !important; border: 1px solid #00f2fe; border-radius:8px; padding:6px 10px; display:inline-block; overflow:hidden; width: fit-content; max-width: 100%;}
    .bg-twitter { background-color: #0a0a0a !important; border: 1px solid #555; border-radius:8px; padding:6px 10px; display:inline-block; overflow:hidden; width: fit-content; max-width: 100%;}
    .bg-instagram { background: linear-gradient(135deg, #4a1c40, #5c2018) !important; border: 1px solid #fd1d1d; border-radius:8px; padding:6px 10px; display:inline-block; overflow:hidden; width: fit-content; max-width: 100%;}
    .bg-other { background-color: #2a2a2a !important; border: 1px solid #777; border-radius:8px; padding:6px 10px; display:inline-block; overflow:hidden; width: fit-content; max-width: 100%;}

    /* Líneas divisorias verticales (Gris Opaco Elegante) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2),
    div[data-testid="stHorizontalBlock"] > div:nth-child(3),
    div[data-testid="stHorizontalBlock"] > div:nth-child(4),
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) {
        border-left: 2px solid rgba(255, 255, 255, 0.1) !important;
        padding-left: 15px !important;
    }

    .row-title { font-weight: bold; font-size: 1.1em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: white;}
    .row-url { font-size: 0.8em; color: #00d2ff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 5px;}
    
    /* Download Button */
    [data-testid="stButton"] button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 50px !important;
        width: 100% !important;
        font-size: 18px !important;
    }
    
    /* Efecto parpadeo verde suave */
    @keyframes blinking-green {
        0% { background-color: #28a745; box-shadow: 0 0 5px #28a745; }
        50% { background-color: #34ce57; box-shadow: 0 0 20px #34ce57; }
        100% { background-color: #28a745; box-shadow: 0 0 5px #28a745; }
    }
    .st-emotion-cache-pulse button {
        animation: blinking-green 1.5s infinite !important;
    }

    /* Estilo para el botón de Log (que parece barra) */
    .st-emotion-cache-logbar button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        text-align: left !important;
        justify-content: flex-start !important;
        height: 45px !important;
        font-size: 0.9em !important;
    /* Logs Flotantes que se superponen */
    .logs-wrapper {
        position: relative;
        height: 38px;
        width: 100%;
        z-index: 999;
    }
    details {
        width: 100%;
        position: absolute;
        z-index: 1000;
    }
    summary {
        background-color: rgba(0, 210, 255, 0.1);
        border: 1px solid #00d2ff;
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 0.75rem;
        color: #00d2ff;
        cursor: pointer;
        list-style: none;
        height: 35px;
        display: flex;
        align-items: center;
        gap: 5px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    summary::-webkit-details-marker {
        display: none;
    }
    .logs-content {
        background-color: #1c1a29;
        border: 1px solid rgba(0, 210, 255, 0.5);
        border-radius: 6px;
        padding: 8px;
        max-height: 150px;
        overflow-y: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.8);
        margin-top: 2px;
    }
    .log-entry {
        font-size: 0.7rem;
        color: #ccc;
        margin-bottom: 3px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND SUPPORT ---
def format_duration(seconds):
    if not seconds: return ""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"

def is_facebook(link):
    return any(domain in link.lower() for domain in ['facebook.com', 'fb.watch', 'fb.com'])

def sanitize_facebook_url(url, log_cont=None):
    if '/share/' in url:
        try:
            session = requests.Session()
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
            response = session.head(url, headers=headers, allow_redirects=True, timeout=10)
            url = response.url
        except: pass
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    video_id = None
    if 'v' in qs: video_id = qs['v'][0]
    elif 'story_fbid' in qs: video_id = qs['story_fbid'][0]
    else:
        match = re.search(r'/(?:reel|reels|watch|videos)/(?:[^/]+/)?(\d+)', parsed.path)
        if match: video_id = match.group(1)
        else:
            match_id = re.search(r'(\d{12,})', url)
            if match_id: video_id = match_id.group(1)
    if video_id: return f"https://www.facebook.com/video.php?v={video_id}"
    return urllib.parse.urlunparse(parsed._replace(query=""))

def cobalt_download(fb_url, is_audio, log_cont):
    return None, None # API muerta

def organic_scraper(fb_url, is_audio, log_cont):
    native_headers = {'User-Agent': 'FacebookApp/450.0.0.44.109 [FBAN/MessengerLite;FBAV/450.0.0.44.109;FBPN/com.facebook.mlite;FBLC/es_ES;FBBV/574844853]'}
    try:
        video_id = "fb_video"
        id_match = re.search(r'/(?:reel|reels|watch|videos)/(?:[^/]+/)?(\d+)', fb_url)
        if id_match: video_id = id_match.group(1)
        res_main = requests.get(fb_url, headers=native_headers, timeout=15, verify=False)
        html_data = res_main.text
        video_url = None
        for pattern in [r'"hd_src":"([^"]+)"', r'"sd_src":"([^"]+)"', r'"playable_url":"([^"]+)"']:
            match = re.search(pattern, html_data)
            if match:
                video_url = match.group(1).replace('\\/', '/').encode().decode('unicode_escape')
                break
        if video_url:
            ext = "mp3" if is_audio else "mp4"
            final_name = f"downloads/{video_id}.{ext}"
            v_res = requests.get(video_url, headers=native_headers, stream=True, timeout=60)
            with open(final_name, "wb") as f:
                for chunk in v_res.iter_content(chunk_size=8192): f.write(chunk)
            return final_name, {"title": f"FB ({video_id})"}
    except: pass
    return None, None

@st.cache_data(ttl=3600, show_spinner=False)
def _cached_playwright_sniffer_v4(fb_url, user_agent):
    try:
        from playwright.sync_api import sync_playwright
        from playwright_stealth import Stealth
        with Stealth().use_sync(sync_playwright()) as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()
            page.goto(fb_url, timeout=30000)
            page.wait_for_timeout(5000)
            html_data = page.content()
            browser.close()
            video_url = None
            for pattern in [r'"browser_native_hd_url":"([^"]+)"', r'"browser_native_sd_url":"([^"]+)"', r'"hd_src":"([^"]+)"', r'"sd_src":"([^"]+)"', r'"playable_url":"([^"]+)"']:
                match = re.search(pattern, html_data)
                if match:
                    video_url = match.group(1).replace('\\/', '/').encode().decode('unicode_escape')
                    break
            return video_url, None
    except Exception as e: return None, str(e)

def playwright_scraper(fb_url, is_audio, log_cont, user_agent):
    with log_cont: st.info("👻 Playwright Stealth...")
    sniffed_url, err = _cached_playwright_sniffer_v4(fb_url, user_agent)
    return sniffed_url

def descargar_yt_dlp(opciones, dl_url):
    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(dl_url, download=True)
        filename = ydl.prepare_filename(info)
        if "postprocessors" in opciones or "Audio" in str(opciones):
             if not filename.endswith(".mp3"):
                 filename = os.path.splitext(filename)[0] + ".mp3"
        return filename, info

# --- ESTADO ---
if 'links' not in st.session_state:
    st.session_state.links = []
if 'input_url' not in st.session_state:
    st.session_state.input_url = ""

def get_platform(url):
    u = url.lower()
    if 'youtube.com' in u or 'youtu.be' in u: return 'youtube', '▶️'
    if 'facebook.com' in u or 'fb.watch' in u or 'fb.com' in u: return 'facebook', '📘'
    if 'twitter.com' in u or 'x.com' in u: return 'twitter', '🐦'
    if 'tiktok.com' in u: return 'tiktok', '🎵'
    if 'instagram.com' in u: return 'instagram', '📸'
    return 'other', '🌐'

def add_link():
    url = st.session_state.url_input_field.strip()
    if url:
        # Check if already exists
        if not any(l['url'] == url for l in st.session_state.links):
            plat, icon = get_platform(url)
            # Try to get metadata
            is_dead = False
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'extractor_args': {'youtube': {'player_client': ['android']}}}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Video Desconocido')
                    thumb = info.get('thumbnail', 'https://via.placeholder.com/150x100?text=No+Thumb')
                    duration = info.get('duration', 0)
            except:
                title = "Video retirado de la plataforma"
                thumb = "https://via.placeholder.com/150x100?text=Retirado"
                duration = 0
                is_dead = True
                
            st.session_state.links.append({
                'url': url,
                'title': f"{icon} {title}",
                'thumbnail': thumb,
                'platform': plat,
                'duration': duration,
                'downloading': False,
                'completed': False,
                'is_dead': is_dead,
                'ready_to_process': False,
                'file_path': None,
                'last_log': 'Listo para procesar' if not is_dead else '⚠️ Video no disponible',
                'logs': ['✅ Enlace verificado y listo'] if not is_dead else ['❌ Error: El video no pudo ser extraído']
            })
        st.session_state.url_input_field = ""

# --- INTERFAZ ---
st.title("TDwnuXTw ®")
st.markdown("### | Adquisidor de videos multiplataforma")

st.text_input("🔗 Pega los enlaces aquí:", key="url_input_field", on_change=add_link)

if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Renderizar Filas
platform_styles = {
    'youtube': {'bg': '#5a0a0a', 'border': '#ff0000'},
    'facebook': {'bg': '#0b1c3c', 'border': '#1877F2'},
    'tiktok': {'bg': 'linear-gradient(135deg, #000, #111)', 'border': '#00f2fe'},
    'twitter': {'bg': '#0a0a0a', 'border': '#555'},
    'instagram': {'bg': 'linear-gradient(135deg, #4a1c40, #5c2018)', 'border': '#fd1d1d'},
    'other': {'bg': '#2a2a2a', 'border': '#777'}
}

if st.session_state.links:
    dynamic_css = "<style>\n"
    for i, link_data in enumerate(st.session_state.links):
        plat = link_data['platform']
        p_style = platform_styles.get(plat, platform_styles['other'])
        
        dynamic_css += f"""
        div[data-testid="stHorizontalBlock"]:nth-of-type({i+1}) div[data-testid="stRadio"] label[data-baseweb="radio"] {{
            background: {p_style['bg']} !important;
            border: 1px solid {p_style['border']} !important;
            opacity: 0.6;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        div[data-testid="stHorizontalBlock"]:nth-of-type({i+1}) div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {{
            opacity: 1.0 !important;
            box-shadow: 0 0 10px {p_style['border']} !important;
            border: 1px solid {p_style['border']} !important;
        }}
        """
    dynamic_css += "</style>"
    st.markdown(dynamic_css, unsafe_allow_html=True)

for i, link_data in enumerate(st.session_state.links):
    plat = link_data['platform']
    bg_class = f"bg-{plat}"
    
    col_thumb, col_info, col_av, col_qual, col_btn = st.columns([1.2, 4, 1.5, 2, 1])
    
    with col_thumb:
        dur_str = format_duration(link_data.get('duration', 0))
        dur_html = f'<div style="position: absolute; bottom: 5px; right: 5px; background: rgba(0,0,0,0.8); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75em; font-weight: bold; border: 1px solid rgba(255,255,255,0.2);">{dur_str}</div>' if dur_str else ""
        
        # Icono de imagen no cargada (🖼️) como fallback
        fallback_img = "https://via.placeholder.com/150x100?text=%F0%9F%96%BC%EF%B8%8F"
        
        st.markdown(f"""
            <div style="position: relative; height: 100px; width: 100%; display: flex; align-items: center; justify-content: center; overflow: hidden; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background-color: #0e1117;">
                <img src="{link_data['thumbnail']}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.onerror=null;this.src='{fallback_img}';">
                {dur_html}
            </div>
        """, unsafe_allow_html=True)
        
    with col_info:
        title_style = "font-style: italic; color: #aaa;" if link_data.get('is_dead') else "color: white;"
        st.markdown(f"""
            <div style="height: 100px; display: flex; flex-direction: column; justify-content: center;">
                <div class="row-title" style="margin-bottom: 6px; {title_style}">{link_data['title']}</div>
                <div class="{bg_class}">
                    <div class="row-url" style="margin-top: 0px;">{link_data['url']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_av:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        fmt = st.radio("Formato", ["Video (MP4)", "Audio (MP3)"], label_visibility="collapsed", key=f"fmt_{i}")
        
    with col_qual:
        log_ph = st.empty()
        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        
        if "Video" in fmt:
            qual = st.selectbox("Calidad", ["1080p", "720p", "480p", "360p", "240p", "144p"], label_visibility="collapsed", key=f"q_{i}")
            rate = {"1080p": 391, "720p": 187, "480p": 100, "360p": 62, "240p": 37, "144p": 12}.get(qual, 100)
        else:
            qual = st.selectbox("Calidad", ["320 Kbps", "256 Kbps", "128 Kbps"], label_visibility="collapsed", key=f"q_{i}")
            rate = {"320 Kbps": 40, "256 Kbps": 32, "128 Kbps": 16}.get(qual, 32)
        
        current_log = link_data.get('last_log', 'Esperando...')
            
    with col_btn:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        btn_ph = st.empty()

    should_start = False

    if link_data.get('completed'):
        with log_ph.container():
            latest = link_data.get('last_log', 'Completado')
            log_html = f'''
            <div class="logs-wrapper">
                <details>
                    <summary>✅ {latest}</summary>
                    <div class="logs-content">
            '''
            if 'logs' in link_data:
                for msg in link_data['logs']:
                    log_html += f'<div class="log-entry">✓ {msg}</div>'
            log_html += '</div></details></div>'
            st.markdown(log_html, unsafe_allow_html=True)
        with btn_ph.container():
            with open(link_data['file_path'], "rb") as f:
                st.download_button("💾 Guardar", data=f, file_name=os.path.basename(link_data['file_path']), mime="video/mp4" if "Video" in fmt else "audio/mpeg", key=f"save_{i}")
    else:
        with log_ph.container():
            st.markdown('<div class="st-emotion-cache-logbar">', unsafe_allow_html=True)
            clicked = st.button(f"▶ {current_log}", key=f"trigger_{i}", use_container_width=True, disabled=link_data.get('is_dead'))
            st.markdown('</div>', unsafe_allow_html=True)
        if clicked and not link_data.get('is_dead'):
            should_start = True

    if should_start:
        log_ph.empty()
        btn_ph.empty()
        
        with log_ph.container():
            log_container = st.empty()
                
        with btn_ph.container():
            st.markdown('<div class="st-emotion-cache-pulse">', unsafe_allow_html=True)
            st.button("⚙️", key=f"proc_{i}", disabled=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # LOGICA DE DESCARGA
        link_data['downloading'] = True
        def update_log(msg):
            # Filtrar porcentajes intermedios
            if "Descargando" in msg:
                if "100%" not in msg:
                    # Si ya hay un "Descargando..." sin 100%, no lo duplicamos
                    if any("Descargando" in l and "100%" not in l for l in link_data.get('logs', [])):
                        return
            
            link_data['last_log'] = msg
            if 'logs' not in link_data: link_data['logs'] = []
            link_data['logs'].append(msg)
            
            with log_container: 
                log_html = f'''
                <div class="logs-wrapper">
                    <details>
                        <summary>⚙️ {msg}</summary>
                        <div class="logs-content">
                '''
                for l in link_data['logs']:
                    log_html += f'<div class="log-entry">⚡ {l}</div>'
                log_html += '</div></details></div>'
                st.markdown(log_html, unsafe_allow_html=True)

        def local_hook(d):
            if d['status'] == 'downloading':
                p = d.get('_percent_str', '0%')
                if '100%' in p:
                    update_log(f"Descarga finalizada (100%)")
                else:
                    update_log("Descargando...")
                
        update_log("Iniciando...")
        
        is_audio = "Audio" in fmt
        UAS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0']
        selected_ua = UAS[0]
        ydl_opts = {
            'progress_hooks': [local_hook],
            'outtmpl': f'downloads/%(title).50s_{i}.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'http_headers': {'User-Agent': selected_ua}
        }
        
        if os.path.exists('temp_cookies.txt'):
            ydl_opts['cookiefile'] = 'temp_cookies.txt'
        
        if is_audio:
            q_val = qual.split(' ')[0]
            ydl_opts.update({
                'format': 'bestaudio/best', 
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': q_val}]
            })
        else:
            q_val = qual.replace('p', '')
            ydl_opts.update({
                'format': f'bestvideo[height<={q_val}][ext=mp4]+bestaudio[ext=m4a]/best[height<={q_val}][ext=mp4]/best', 
                'merge_output_format': 'mp4'
            })
            
        filename = None
        raw_url = link_data['url']
        is_fb = is_facebook(raw_url)
        
        try:
            if is_fb:
                ydl_opts['http_headers'].update({'Sec-Fetch-Dest': 'video', 'Origin': 'https://www.facebook.com'})
            elif "youtube" in raw_url:
                if 'http_headers' in ydl_opts: del ydl_opts['http_headers']
                ydl_opts['extractor_args'] = {'youtube': {'player_client': ['android']}}
                
            update_log("⚡ Nivel 1: yt-dlp...")
            try:
                filename, _ = descargar_yt_dlp(ydl_opts, raw_url)
            except Exception as e:
                update_log("⚠️ Nivel 1 falló.")
                clean_url = sanitize_facebook_url(raw_url, None) if is_fb else raw_url
                try:
                    if not is_fb and clean_url == raw_url: raise Exception()
                    filename, _ = descargar_yt_dlp(ydl_opts, clean_url)
                except:
                    update_log("⚠️ Nivel 2 falló.")
                    filename, _ = organic_scraper(clean_url, is_audio, None) if is_fb else (None, None)
                    if not filename:
                        update_log("⚠️ Nivel 3 falló.")
                        try:
                            if not is_fb: raise Exception()
                            filename, _ = descargar_yt_dlp(ydl_opts, clean_url)
                        except:
                            update_log("⚠️ Nivel 4 falló.")
                            try:
                                if not is_fb: raise Exception()
                                proxy_res = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000", timeout=10)
                                if proxy_res.status_code == 200:
                                    px = proxy_res.text.strip().split("\\r\\n")[0]
                                    ydl_opts['proxy'] = f"http://{px}"
                                    filename, _ = descargar_yt_dlp(ydl_opts, clean_url)
                                else: raise Exception()
                            except:
                                update_log("⚠️ Nivel 5 falló.")
                                sniffed_url = playwright_scraper(clean_url, is_audio, log_container, selected_ua) if is_fb else None
                                if sniffed_url:
                                    ext = "mp3" if is_audio else "mp4"
                                    filename = f"downloads/pw_{int(time.time())}.{ext}"
                                    v_res = requests.get(sniffed_url, headers={'User-Agent': selected_ua}, stream=True, timeout=60)
                                    with open(filename, "wb") as f:
                                        for chunk in v_res.iter_content(chunk_size=8192): f.write(chunk)
                                else:
                                    update_log("❌ Error total")
                                    
        except Exception as e:
            update_log("Error fatal")
            
        if filename:
            st.session_state.links[i]['completed'] = True
            st.session_state.links[i]['file_path'] = filename
            
            # --- AUTO-BORRADO A LOS 4 MINUTOS ---
            def delayed_delete(p):
                time.sleep(240) # 240 seg = 4 min
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except:
                    pass
            threading.Thread(target=delayed_delete, args=(filename,), daemon=True).start()
            
            st.rerun()
