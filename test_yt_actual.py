import yt_dlp
import sys

url = 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
ydl_opts = {
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1'
    },
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'outtmpl': 'downloads/%(title).50s.%(ext)s',
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print("Success!")
except Exception as e:
    print(f"Error: {e}")
