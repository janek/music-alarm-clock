import requests

url = "http://127.0.0.1:3141/cronsave"

payload = {
    "minutes": 20,
    "hours": 12,
    "mode": "auto",
    "fade_minutes": 3
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())


