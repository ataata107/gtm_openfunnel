import requests
import json

url = "https://google.serper.dev/search"

payload = json.dumps({
  "q": "Find fintech companies using AI for fraud detection",
  "num": 20
})
headers = {
  'X-API-KEY': '3fef2bbee3852ed5117a94560a09b27741f1b771',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.json())