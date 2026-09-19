import requests
URL = "http://localhost:8001/api/convert"
API_KEY = "default_secret_key_123"

def test():
    print("Testing YouTube URL conversion...")
    # Just a random youtube URL (e.g. Rick Astley or something, or any short video)
    # MarkItDown will fetch the transcript using youtube_transcript_api
    response = requests.post(URL, headers={"X-API-Key": API_KEY}, data={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    if response.status_code == 200:
        print("Success!")
        print(response.json()["markdown"][:200] + "...")
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

test()
