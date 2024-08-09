import requests


def fetch_rewards():
    resp = requests.get("https://api.volara.io/v1/stats")
    print(resp.json())
