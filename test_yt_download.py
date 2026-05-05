import yt_dlp
import os

url = 'https://www.youtube.com/watch?v=BaW_jenozKc' # Some short video, e.g., "me at the zoo"
ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'outtmpl': 'downloads/%(title).50s.%(ext)s',
    'quiet': False
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    filename = ydl.prepare_filename(info)
    print("prepare_filename returned:", filename)
    print("Does the file exist?", os.path.exists(filename))
    
    # check if another file with .mp4 exists
    base = os.path.splitext(filename)[0]
    print("Does .mp4 exist?", os.path.exists(base + ".mp4"))
