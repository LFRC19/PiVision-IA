import requests

TOKEN = "7758206368:AAG77jBM8dLjLPfy14ZsOxeUBgdbAsQMYhU"
resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()
print(resp)
