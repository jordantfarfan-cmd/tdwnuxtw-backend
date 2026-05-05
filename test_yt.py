import yt_dlp
import sys

url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
ydl_opts = {
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1'
    }
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print("Success!")
except Exception as e:
    print(f"Error: {e}")
