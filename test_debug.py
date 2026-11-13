import requests
import json

url = "http://127.0.0.1:8000/debug-search"
payload = {"question": "ما هو تعريف الموائع؟"}
response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))