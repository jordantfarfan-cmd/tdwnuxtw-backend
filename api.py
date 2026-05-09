from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os
import time
import threading
import requests
import urllib.parse
import re
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

def extract_video_id_from_url(url):
    try:
        match_id = re.search(r'(\d{8,})', url)
        if match_id:
            return match_id.group(1)
        parsed = urllib.parse.urlparse(url)
        path_segments = [seg for seg in parsed.path.split('/') if seg]
        if path_segments:
            return path_segments[-1]
    except:
        pass
    return ""

def generate_custom_filename(title, url, extension):
    r"""
    Genera un nombre de archivo siguiendo las reglas:
    1. Limpiar símbolos prohibidos: \ / : * ? " < > |
    2. Cortar a 50 caracteres + ... si es necesario.
    3. Añadir marca " - TDwnuXTw® " y sufijo de plataforma.
    """
    # 1. Limpiar símbolos prohibidos por Windows
    clean_title = re.sub(r'[\\/:*?"<>|]', '', title)
    
    # 2. Cortar a 50 caracteres
    truncated = False
    if len(clean_title) > 50:
        clean_title = clean_title[:50].strip()
        truncated = True
    
    # 3. Determinar sufijo de plataforma
    suffix = "WEB"
    u = url.lower()
    if 'facebook.com' in u or 'fb.watch' in u or 'fb.com' in u: suffix = "FB"
    elif 'youtube.com' in u or 'youtu.be' in u: suffix = "YT"
    elif 'twitter.com' in u or 'x.com' in u: suffix = "X"
    elif 'tiktok.com' in u: suffix = "TT"
    elif 'instagram.com' in u: suffix = "IG"
    elif 'linkedin.com' in u: suffix = "LI"
    elif 'pinterest.com' in u or 'pin.it' in u: suffix = "PIN"
    
    # 4. Construir nombre final
    final_name = clean_title
    if truncated:
        final_name += "..."
    
    final_name += f" - TDwnuXTw® {suffix}.{extension}"
    return final_name

# Este archivo es el equivalente a app.py pero diseñado como un "Cerebro API" sin interfaz gráfica
app = FastAPI(title="TDwnuXTw Backend API")

if os.path.exists("public"):
    app.mount("/public", StaticFiles(directory="public"), name="public")
    @app.get("/")
    def serve_index():
        with open("public/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

@app.get("/api/debug/system")
def get_system_info():
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        
        mem_total = 0
        for line in lines:
            if 'MemTotal' in line:
                mem_total = int(line.split()[1]) / (1024 * 1024) # Convertir a GB
                break
        
        return {
            "status": "online",
            "total_ram_gb": round(mem_total, 2),
            "platform": "HuggingFace Spaces (Linux)",
            "cpu_cores": os.cpu_count()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/proxy_image")
def proxy_image(url: str):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        }
        if "instagram" in url.lower():
            headers['Referer'] = 'https://www.instagram.com/'
        elif "licdn.com" in url.lower() or "linkedin" in url.lower():
            headers['Referer'] = 'https://www.linkedin.com/'
            
        res = requests.get(url, headers=headers, timeout=10)
        return Response(content=res.content, media_type=res.headers.get('Content-Type', 'image/jpeg'))
    except Exception as e:
        return Response(content=b"", media_type="image/jpeg", status_code=404)

class DownloadRequest(BaseModel):
    url: str
    format: str
    quality: str
    title: str = "Video"

def delayed_delete(filepath: str):
    time.sleep(240) # 4 minutos
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass

def is_facebook(link):
    return any(domain in link.lower() for domain in ['facebook.com', 'fb.watch', 'fb.com'])

def sanitize_facebook_url(url):
    if '/share/' in url:
        try:
            session = requests.Session()
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36'}
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

def organic_scraper(fb_url, is_audio):
    native_headers = {'User-Agent': 'FacebookApp/450.0.0.44.109 [FBAN/MessengerLite;FBAV/450.0.0.44.109;FBPN/com.facebook.mlite]'}
    try:
        import uuid
        video_id = f"fb_video_{uuid.uuid4().hex[:8]}"
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
            return final_name
    except: pass
    return None

def get_free_proxy():
    import random
    try:
        # Peticion a proxyscrape para proxies HTTP (anonimos y soportando SSL)
        proxy_res = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all", timeout=5)
        if proxy_res.status_code == 200:
            proxies = proxy_res.text.strip().split("\r\n")
            if proxies and len(proxies) > 0 and proxies[0] != "":
                px = random.choice(proxies)
                return f"http://{px}"
    except:
        pass
    return None

def descargar_yt_dlp(opciones, dl_url):
    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(dl_url, download=True)
        filename = ydl.prepare_filename(info)
        if "postprocessors" in opciones or "Audio" in str(opciones):
             if not filename.endswith(".mp3"):
                 filename = os.path.splitext(filename)[0] + ".mp3"
        return filename, info.get('title', 'Video')

@app.post("/api/info")
async def api_info(req: DownloadRequest):
    raw_url = req.url
    is_fb = is_facebook(raw_url)
    
    # Sanitizar URL si es Facebook
    if is_fb:
        raw_url = sanitize_facebook_url(raw_url)
        
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_color': True,
        'extract_flat': False,
    }
    
    if is_fb:
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36',
            'Sec-Fetch-Dest': 'video', 
            'Origin': 'https://www.facebook.com'
        }
    elif "youtube" in raw_url or "youtu.be" in raw_url:
        ydl_opts['extractor_args'] = {'youtube': {'player_client': ['android', 'ios']}}
    
    # Usar cookies si existen (importante para evitar bloqueos)
    if os.path.exists('temp_cookies.txt'):
        ydl_opts['cookiefile'] = 'temp_cookies.txt'
    
    try:
        info = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(raw_url, download=False)
        except Exception as e_info:
            if "youtube" in raw_url or "youtu.be" in raw_url:
                print("Info normal falló, buscando proxy...")
                proxy = get_free_proxy()
                if proxy:
                    ydl_opts['proxy'] = proxy
                    print(f"Reintentando con proxy: {proxy}")
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_proxy:
                        info = ydl_proxy.extract_info(raw_url, download=False)
                else:
                    raise e_info
            else:
                raise e_info
                
        thumb = info.get('thumbnail', 'https://placehold.co/150x100/000000/FFFFFF/png?text=No+Thumb')
        # Proxy Instagram and LinkedIn thumbnails to bypass CORS/Hotlink protection
        if ("instagram" in raw_url.lower() or "linkedin.com" in raw_url.lower()) and thumb.startswith("http"):
            thumb = f"/api/proxy_image?url={urllib.parse.quote(thumb)}"

        title = info.get('title', 'Video Desconocido')
        desc = info.get('description', '')
        
        if is_fb:
            # Si FB devuelve algo genérico o vacío, usamos la descripción
            if title == 'Video' or not title or title == 'Video Desconocido':
                title = desc if desc else 'Video de Facebook'
            elif desc and len(desc) > len(title) and title in desc:
                title = desc
        elif "instagram" in raw_url.lower():
            if desc:
                title = desc
            elif title.startswith('Video by'):
                title = title.replace('Video by', 'Video de Instagram de')
            elif title == 'Video':
                title = 'Video de Instagram'
        elif "pinterest" in raw_url.lower() or "pin.it" in raw_url.lower():
            clean_title = title.strip() if title else ""
            is_generic = not clean_title or clean_title.lower() in [
                "pinterest video", "pinterest pin", "video", "video desconocido", "pin"
            ] or clean_title.startswith("Pinterest video #") or clean_title.startswith("Pinterest Pin #")
            
            if not is_generic:
                title = clean_title
            elif desc and not any(phrase in desc.lower() for phrase in ["this pin was created by", "descubrió este pin"]):
                title = desc
            else:
                video_id = extract_video_id_from_url(raw_url)
                if video_id:
                    title = f"Video de Pinterest {video_id}"
                else:
                    title = "Video de Pinterest"

        # Limpiar saltos de línea para mostrarlo en una sola línea
        if title:
            title = title.replace('\n', ' ').replace('\r', ' ')

        return {
            "title": title,
            "thumbnail": thumb,
            "duration": info.get('duration', 0),
            "status": "success"
        }
    except Exception as e:
        print(f"Error en api_info: {str(e)}")
        return {
            "title": "Video protegido o enlace inválido", 
            "thumbnail": "https://placehold.co/150x100/000000/FFFFFF/png?text=Error", 
            "duration": 0,
            "status": "error",
            "detail": str(e)
        }

@app.post("/api/download")
async def api_download(req: DownloadRequest, bg_tasks: BackgroundTasks):
    if not os.path.exists('downloads'): os.makedirs('downloads')
    
    raw_url = req.url
    is_audio = "Audio" in req.format
    qual = req.quality
    is_fb = is_facebook(raw_url)
    
    # Sanitizar URL upfront
    if is_fb:
        raw_url = sanitize_facebook_url(raw_url)
    
    ydl_opts = {
        'outtmpl': f'downloads/%(id)s_api.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36'}
    }
    
    if os.path.exists('temp_cookies.txt'):
        ydl_opts['cookiefile'] = 'temp_cookies.txt'
        
    if is_audio:
        q_val = qual.split(' ')[0] if ' ' in qual else qual
        ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': q_val}]})
    else:
        q_val = qual.replace('p', '')
        fmt_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        ydl_opts.update({
            'format': fmt_str,
            'format_sort': [f'res:{q_val}', 'ext:mp4:m4a'],
            'merge_output_format': 'mp4'
        })
        
    filename = None
    title_obtained = "Video"
    
    try:
        if is_fb:
            ydl_opts['http_headers'].update({'Sec-Fetch-Dest': 'video', 'Origin': 'https://www.facebook.com'})
        elif "youtube" in raw_url or "youtu.be" in raw_url:
            if 'http_headers' in ydl_opts: del ydl_opts['http_headers']
            ydl_opts['extractor_args'] = {'youtube': {'player_client': ['android', 'ios']}}
            
        # Nivel 1: Intento directo
        try:
            filename, title_obtained = descargar_yt_dlp(ydl_opts, raw_url)
        except Exception as err_dl:
            # Nivel 2 para YT: Usar Proxy
            if "youtube" in raw_url or "youtu.be" in raw_url:
                print("Descarga directa falló, buscando proxy...")
                proxy = get_free_proxy()
                if proxy:
                    ydl_opts['proxy'] = proxy
                    print(f"Reintentando descarga con proxy: {proxy}")
                    try:
                        filename, title_obtained = descargar_yt_dlp(ydl_opts, raw_url)
                    except Exception as err_proxy:
                        raise HTTPException(status_code=500, detail="Fallo en descarga con proxy: " + str(err_proxy))
                else:
                    raise HTTPException(status_code=500, detail="No se pudo obtener un proxy para intentar descargar el video")
            # Nivel 2: Scraper orgánico (solo para Facebook)
            elif is_fb:
                filename = organic_scraper(raw_url, is_audio)
                title_obtained = "Facebook Video"
            
            if not filename:
                raise HTTPException(status_code=500, detail="No se pudo procesar el video con los métodos disponibles")
                
    except Exception as e:
        print(f"Error en api_download: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    if filename and os.path.exists(filename):
        bg_tasks.add_task(delayed_delete, filename)
        
        # Generar nombre personalizado para el usuario
        ext = "mp3" if is_audio else "mp4"
        actual_title = req.title if req.title and req.title != "Video" else title_obtained
        
        generic_titles = ["video", "video desconocido", "video de facebook", "facebook video", "video de instagram", "video de tiktok", "video de pinterest"]
        if actual_title.lower().strip() in generic_titles:
            video_id = extract_video_id_from_url(req.url)
            if video_id:
                actual_title = f"{actual_title.strip()} {video_id}"
                
        display_name = generate_custom_filename(actual_title, req.url, ext)
        
        return FileResponse(filename, media_type="video/mp4" if not is_audio else "audio/mpeg", filename=display_name)
    
    raise HTTPException(status_code=500, detail="Error desconocido en el servidor")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "El motor Python está encendido"}
