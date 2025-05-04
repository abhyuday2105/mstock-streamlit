import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

# असली credentials डालें
API_KEY = "यहाँ_अपनी_असली_API_KEY_डालें"
PRIVATE_KEY = "यहाँ_अपनी_PRIVATE_KEY_डालें"
CLIENT_CODE = "यहाँ_CLIENT_CODE_डालें"
PASSWORD = "यहाँ_PASSWORD_डालें"

def get_option_chain_master(exchange):
    url = f"https://api.mstock.trade/openapi/typeb/getoptionchainmaster/{exchange}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-Mirae-Version": "1",
        "X-PrivateKey": PRIVATE_KEY,
        "Content-Type": "application/json"
    }
    res = requests.get(url, headers=headers)
    return res.json()

def fetch_option_chain(exchange, expiry, token):
    url = f"https://api.mstock.trade/openapi/typeb/getoptionchainmaster/{exchange}/{expiry}/{token}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-Mirae-Version": "1",
        "X-PrivateKey": PRIVATE_KEY,
        "Content-Type": "application/json"
    }
    res = requests.get(url, headers=headers)
    return res.json()

def fetch_intraday_candles(symbol):
    url = "https://api.mstock.trade/openapi/typeb/instruments/instruments/intraday"
    payload = {
        "exchange": "1",
        "symbolname": symbol,
        "interval": "THREE_MINUTE"
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-Mirae-Version": "1",
        "X-PrivateKey": PRIVATE_KEY,
        "Content-Type": "application/json"
    }
    res = requests.post(url, json=payload, headers=headers)
    return res.json()

st.set_page_config(layout="wide")
st.title("📊 M.Stock Live Option Chain + Candle Dashboard")

tab1, tab2 = st.tabs(["📈 Option Chain", "🕒 3-Min Candles"])

# Load master data once
st.sidebar.markdown("### Loading Symbol List...")
master_data = get_option_chain_master("NSE")

# Debug: Uncomment to see API response
# st.write(master_data)

symbol_list = sorted(list(set(item["symbolname"] for item in master_data.get("data", []))))
if not symbol_list:
    st.error("No symbols found in option chain master! Check your API credentials.")
    st.stop()

symbol_input = st.sidebar.selectbox("Select Symbol", symbol_list)
symbol_tokens = {}
expiries = []

for item in master_data.get("data", []):
    if item["symbolname"] == symbol_input:
        symbol_tokens[item["expiry"]] = item["token"]
        expiries.append(item["expiry"])

if not expiries:
    st.error("No expiries found for this symbol!")
    st.stop()

selected_expiry = st.sidebar.selectbox("Select Expiry", expiries)
selected_token = symbol_tokens[selected_expiry]

option_data = fetch_option_chain("NSE", selected_expiry, selected_token)

with tab1:
    st.subheader(f"📈 Option Chain: {symbol_input} – {selected_expiry}")
    try:
        calls = pd.DataFrame(option_data["data"]["CE"])
        puts = pd.DataFrame(option_data["data"]["PE"])
        calls = calls[["strikePrice", "lastPrice", "changeinOpenInterest", "impliedVolatility"]]
        puts = puts[["strikePrice", "lastPrice", "changeinOpenInterest", "impliedVolatility"]]
        col1, col2 = st.columns(2)
        col1.markdown("**Calls**")
        col1.dataframe(calls.sort_values("strikePrice"))
        col2.markdown("**Puts**")
        col2.dataframe(puts.sort_values("strikePrice"))
    except Exception as e:
        st.warning(f"Error fetching option chain data: {str(e)}")

candle_data = fetch_intraday_candles(symbol_input)

with tab2:
    st.subheader(f"🕒 3-Minute Candles: {symbol_input}")
    try:
        candles = pd.DataFrame(candle_data["data"]["candles"], columns=["time", "open", "high", "low", "close", "volume"])
        candles["time"] = pd.to_datetime(candles["time"])
        candles.sort_values("time", inplace=True)
        fig = go.Figure(data=[go.Candlestick(
            x=candles["time"],
            open=candles["open"],
            high=candles["high"],
            low=candles["low"],
            close=candles["close"]
        )])
        fig.update_layout(title=f"{symbol_input} – 3-Min Candles", xaxis_title="Time", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Error fetching candle data: {str(e)}")
