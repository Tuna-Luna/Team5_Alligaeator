import requests

url = "http://localhost:8000/detect"

response = requests.post(url)

if response.status_code == 200:
    print("✅ 성공:")
    print(response.json())
else:
    print("❌ 실패:")
    print(response.status_code, response.text)
