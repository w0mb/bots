import requests

url = f"https://api.telegram.org/bot7378367346:AAHdke_WxuNo3diBp2bQvQStdgGqKIT3gfY/setWebhook"
params = {
    "url": "https://193.124.117.17/webhook"  # Укажите правильный URL
}

response = requests.get(url, params=params)
print(response.json())
