import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
import pytz

st.set_page_config(page_title="Market Dashboard", layout="wide")

st.title("📈 Live Market Dashboard")

# -----------------------------
# IST TIME
# -----------------------------
IST = pytz.timezone("Asia/Kolkata")
now = datetime.now(IST).time()

market_open = time(9,15)
market_close = time(15,30)

if market_open <= now <= market_close:
    st.success("🟢 Market Open (NSE)")
else:
    st.info("🔴 Market Closed — Showing Last Trading Data")

# -----------------------------
# NIFTY 50 STOCK LIST
# -----------------------------
stocks = {
"Adani Enterprises": "ADANIENT.NS",
"Adani Ports": "ADANIPORTS.NS",
"Asian Paints": "ASIANPAINT.NS",
"Apollo Hospitals": "APOLLOHOSP.NS",
"Axis Bank": "AXISBANK.NS",
"Bajaj Auto": "BAJAJ-AUTO.NS",
"Bajaj Finance": "BAJFINANCE.NS",
"Bajaj Finserv": "BAJAJFINSV.NS",
"Bharti Airtel": "BHARTIARTL.NS",
"BPCL": "BPCL.NS",
"Britannia": "BRITANNIA.NS",
"Cipla": "CIPLA.NS",
"Coal India": "COALINDIA.NS",
"Divis Labs": "DIVISLAB.NS",
"Dr Reddys": "DRREDDY.NS",
"Eicher Motors": "EICHERMOT.NS",
"Grasim": "GRASIM.NS",
"HCL Tech": "HCLTECH.NS",
"HDFC Bank": "HDFCBANK.NS",
"HDFC Life": "HDFCLIFE.NS",
"Hero MotoCorp": "HEROMOTOCO.NS",
"Hindalco": "HINDALCO.NS",
"HUL": "HINDUNILVR.NS",
"ICICI Bank": "ICICIBANK.NS",
"IndusInd Bank": "INDUSINDBK.NS",
"Infosys": "INFY.NS",
"ITC": "ITC.NS",
"JSW Steel": "JSWSTEEL.NS",
"Kotak Bank": "KOTAKBANK.NS",
"L&T": "LT.NS",
"Mahindra & Mahindra": "M&M.NS",
"Maruti Suzuki": "MARUTI.NS",
"Nestle India": "NESTLEIND.NS",
"NTPC": "NTPC.NS",
"ONGC": "ONGC.NS",
"Power Grid": "POWERGRID.NS",
"Reliance": "RELIANCE.NS",
"SBI": "SBIN.NS",
"SBI Life": "SBILIFE.NS",
"Shriram Finance": "SHRIRAMFIN.NS",
"Sun Pharma": "SUNPHARMA.NS",
"Tata Consumer": "TATACONSUM.NS",
"Tata Motors": "TATAMOTORS.NS",
"Tata Steel": "TATASTEEL.NS",
"TCS": "TCS.NS",
"Tech Mahindra": "TECHM.NS",
"Titan": "TITAN.NS",
"UltraTech Cement": "ULTRACEMCO.NS",
"Wipro": "WIPRO.NS"
}

# -----------------------------
# SIDEBAR
# -----------------------------
stock_name = st.sidebar.selectbox("Select Stock", list(stocks.keys()))
custom = st.sidebar.text_input("Or Enter Custom Ticker")

ticker = custom.upper() if custom else stocks[stock_name]

st.sidebar.write("Ticker:", ticker)

# -----------------------------
# FETCH DATA
# -----------------------------
@st.cache_data(ttl=60)
def get_data(symbol):

    try:

        data = yf.download(symbol, period="7d", interval="5m")

        if data is None or data.empty:
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if "Close" not in data.columns:
            return pd.DataFrame()

        data = data.dropna(subset=["Close"])

        return data

    except:
        return pd.DataFrame()

data = get_data(ticker)

# -----------------------------
# LIVE PRICE
# -----------------------------
if not data.empty and len(data) >= 2:

    latest = float(data["Close"].iloc[-1])
    prev = float(data["Close"].iloc[-2])

    change = latest - prev
    pct = change / prev * 100

    st.metric(
        label=f"{ticker} Price",
        value=f"{latest:.2f}",
        delta=f"{change:.2f} ({pct:.2f}%)"
    )

    last_time = data.index[-1]

    st.caption(f"Last Market Update: {last_time}")

else:
    st.warning("Market data unavailable")

# -----------------------------
# CANDLESTICK CHART
# -----------------------------
st.subheader("Candlestick Chart")

if not data.empty:

    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"]
    )])

    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# YAHOO FINANCE NEWS
# -----------------------------
st.subheader("Latest Market News")

try:

    t = yf.Ticker(ticker)

    news = t.news

    if news:

        for item in news[:5]:

            st.markdown(f"**{item['title']}**")

            st.write(item["publisher"])

            st.write(item["link"])

            st.write("---")

    else:
        st.info("No news available")

except:

    st.info("News unavailable")

# -----------------------------
# TOP NIFTY MOVERS (FAST)
# -----------------------------
st.subheader("Top NIFTY Movers")

symbols = list(stocks.values())

try:

    df = yf.download(symbols, period="2d", interval="1d", group_by="ticker")

    results = []

    for name, symbol in stocks.items():

        if symbol in df.columns.levels[0]:

            d = df[symbol]

            if len(d) >= 2:

                change = d["Close"].iloc[-1] - d["Close"].iloc[-2]

                pct = change / d["Close"].iloc[-2] * 100

                results.append((name, pct))

    movers = pd.DataFrame(results, columns=["Stock","Change %"])

    gainers = movers.sort_values("Change %", ascending=False).head(5)

    losers = movers.sort_values("Change %").head(5)

    col1, col2 = st.columns(2)

    col1.subheader("Top Gainers")
    col1.dataframe(gainers, use_container_width=True)

    col2.subheader("Top Losers")
    col2.dataframe(losers, use_container_width=True)

except:

    st.warning("Unable to calculate movers")
