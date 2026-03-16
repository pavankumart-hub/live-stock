import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
import pytz

# st.set_page_config(
#     page_title="Livestock Sector Future",  # Your app name
#     page_icon="🌿",
#     layout="wide"
# )
# # ✅ STEP 2 - Put hiding code right here
# st.markdown("""
#     <style>
#         /* Hide bottom right Streamlit icons - 2024 class names */
#         .st-emotion-cache-zq5wmm {display: none !important;}
#         .st-emotion-cache-1dp5vir {display: none !important;}
#         .st-emotion-cache-14xtw13 {display: none !important;}
#         .st-emotion-cache-13ln4jf {display: none !important;}
        
#         /* Hide all bottom right buttons */
#         [data-testid="stToolbar"] {display: none !important;}
#         [data-testid="stToolbarActions"] {display: none !important;}
        
#         /* Wildcard - catches any new class names */
#         section[data-testid="stSidebar"] ~ div > div:last-child {
#             display: none !important;
#         }
#     </style>
# """, unsafe_allow_html=True)
# # ✅ STEP 3 - Your actual app code starts here
# # rest of your code...
# # Hide all Streamlit branding
# hide_streamlit_style = """
#     <style>
#         #MainMenu {visibility: hidden;}
#         header {visibility: hidden;}
#         footer {visibility: hidden;}
#         .stDeployButton {display: none;}
#     </style>
# """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# AUTO REFRESH EVERY 15 SECONDS
# st.autorefresh(interval=15000)

# st.title("📈 Live Market Dashboard")

# -----------------------------
# IST TIME
# -----------------------------
IST = pytz.timezone("Asia/Kolkata")
now = datetime.now(IST)
current_time = now.time()

market_open = time(9,15)
market_close = time(15,30)

st.write("Current IST Time:", now.strftime("%d %b %Y %H:%M:%S"))

if market_open <= current_time <= market_close:
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
# SIDEBAR STOCK SELECT
# -----------------------------
stock_name = st.sidebar.selectbox("Select Stock", list(stocks.keys()))
custom = st.sidebar.text_input("Or Enter Custom Ticker")

ticker = custom.upper() if custom else stocks[stock_name]

st.sidebar.write("Ticker:", ticker)

# -----------------------------
# FETCH DATA
# -----------------------------
@st.cache_data(ttl=15)
def get_data(symbol,interval):

    try:

        data = yf.download(symbol, period="7d",interval=interval)

        if data is None or data.empty:
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Convert to IST
        if data.index.tz is None:
            data.index = data.index.tz_localize("UTC")

        data.index = data.index.tz_convert("Asia/Kolkata")

        data = data.dropna(subset=["Close"])

        return data

    except:
        return pd.DataFrame()

data = get_data(ticker,interval="5m")
data1= get_data(ticker,interval="1d")
# -----------------------------
# LIVE PRICE
# -----------------------------
if not data1.empty and len(data) >= 2:

    latest = float(data1["Close"].iloc[-1])
    # st.write(f"Latest 1Close{latest:.2f}")
    prev = float(data1["Close"].iloc[-2])
    # st.write(f"Latest 2Close{prev:.2f}")
    # st.write(item["publisher"])

    change = latest - prev
    pct = change / prev * 100
    col1, col2 = st.columns([2,1])

with col1:
    st.metric(
        label=f"{ticker} Price",
        value=f"{latest:.2f}",
        delta=f"{change:.2f} ({pct:.2f}%)"
    )

with col2:
    last_time = data1.index[-1].strftime("%d %b %Y %H:%M IST")
    st.caption(f"Last Update\n{last_time}")

if data1.empty:
    st.warning("Market data unavailable")
#     st.metric(
#         label=f"{ticker} Price",
#         value=f"{latest:.2f}",
#         delta=f"{change:.2f} ({pct:.2f}%)"
#     )

#     last_time = data1.index[-1].strftime("%d %b %Y %H:%M IST")

#     st.caption(f"Last Market Update: {last_time}")

# else:
#     st.warning("Market data unavailable")

# -----------------------------
# CANDLESTICK CHART (ONE DAY)
# -----------------------------
# st.subheader("Candlestick Chart")

if not data.empty:

    last_day = data.index.date[-1]

    day_data = data[data.index.date == last_day]

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=day_data.index,
        open=day_data["Open"],
        high=day_data["High"],
        low=day_data["Low"],
        close=day_data["Close"]
    ))

    fig.update_layout(
        # title=f"{ticker} Intraday Chart",
        height=400,
        xaxis_rangeslider_visible=False
    )

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
# TOP NIFTY MOVERS
# -----------------------------
st.subheader("Top NIFTY Movers")

symbols = list(stocks.values())

try:

    df = yf.download(symbols, period="3d", interval="1d", group_by="ticker")

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
