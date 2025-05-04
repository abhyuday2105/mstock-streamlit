import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
import json
import http.client

API_KEY = ""
PRIVATE_KEY = "your_private_key"
CLIENT_CODE = "MA80539"
PASSWORD = "Knathdurg#78"

def login_get_refresh_token():
    conn = http.client.HTTPSConnection("api.mstock.trade")
    headers = {
        "X-Mirae-Version": "1",
        "Content-Type": "application/json"
    }
    payload = {
        "clientcode": CLIENT_CODE,
        "password": PASSWORD,
        "totp": "",
        "state": ""
    }
    conn.request("POST", "/openapi/typeb/connect/login", json.dumps(payload), headers)
    res = conn.getresponse()
    data = res.read()
    response = json.loads(data.decode("utf-8"))
    if response.get("status") == "true":
        print("[+] OTP sent. Use it to get access token.")
        return response["data"]["jwtToken"]
    else:
        raise Exception(f"Login failed: {response.get('message')}")

# बाकी फंक्शन्स भी इसी तरह syntax ठीक करें

def main():
    st.set_page_config(layout="wide")
    st.title("📊 M.Stock Live Option Chain + Candle Dashboard")
    # आगे का Streamlit UI और फंक्शन कॉल यहाँ लिखें

if __name__ == "__main__":
    main()
