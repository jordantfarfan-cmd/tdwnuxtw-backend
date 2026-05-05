import requests

fb_url = "https://www.youtube.com/watch?v=wI5b7lDAQKM"
endpoints = ["https://api.cobalt.tools/api/json", "https://cobalt.api.unv.me/api/json", "https://api.geronimo.top/api/json"]
headers = {"Accept": "application/json", "Content-Type": "application/json"}
payload = {"url": fb_url, "videoQuality": "720", "filenameStyle": "classic", "downloadMode": "video"}

for api_url in endpoints:
    print(f"Testing {api_url}...")
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            print("Response:", response.json())
        else:
            print("Response text:", response.text)
    except Exception as e:
        print("Error:", e)
