import requests

fb_url = "https://www.youtube.com/watch?v=wI5b7lDAQKM"
endpoints = ["https://api.cobalt.tools/"]
headers = {"Accept": "application/json", "Content-Type": "application/json"}
payload = {"url": fb_url, "videoQuality": "720", "isAudioOnly": False}

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
