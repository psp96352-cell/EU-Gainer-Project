import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import yfinance as yf

API_URL = "https://eu-gainer-project.onrender.com/get_gainers"

st.set_page_config(page_title="EU Gainer Monitor", layout="wide")
st.title("📈 유럽 급등주 실시간 감시")

# ======================================================
# 🔷 1) 유럽 지수 데이터 가져오기
# ======================================================
def get_eu_indices():
    indices = {
        "^FTSE": "FTSE 100 (영국)",
        "^GDAXI": "DAX (독일)",
        "^FCHI": "CAC 40 (프랑스)",
        "^STOXX50E": "EURO STOXX50 (유럽)"
    }

    data = {}
    for ticker, name in indices.items():
        try:
            df = yf.download(ticker, period="1d", interval="1m", progress=False)

            if df is None or df.empty:
                continue

            df = df.dropna()
            price_now = float(df["Close"].iloc[-1])
            price_open = float(df["Open"].iloc[0])
            change = ((price_now - price_open) / price_open) * 100

            data[name] = {
                "현재가": round(price_now, 2),
                "변동률(%)": round(change, 2)
            }
        except:
            continue

    return data


# ======================================================
# 🔷 2) 종목별 차트 그리기
# ======================================================
def plot_stock_chart(ticker):
    df = yf.download(ticker, period="1d", interval="1m", progress=False)

    if df is None or df.empty:
        st.warning("📉 차트 데이터를 불러올 수 없습니다.")
        return

    df = df.dropna()
    st.line_chart(df["Close"], use_container_width=True)


# ======================================================
# 🔷 사이드바 설정
# ======================================================
st.sidebar.header("⚙ 설정")

interval = st.sidebar.number_input("기준 분", 1, 60, 5)
min_gain = st.sidebar.number_input("📈 상승률 기준 (%)", 0.1, 30.0, 2.0)
top_n = st.sidebar.number_input("📌 Top N 개수", 1, 50, 10)

autorefresh = st.sidebar.toggle("🔄 자동 새로고침", True)
refresh_sec = st.sidebar.slider("새로고침 간격 (초)", 10, 120, 30)

if autorefresh:
    st_autorefresh(interval=refresh_sec * 1000, key="refresh")


# ======================================================
# 🔷 3) 유럽 지수 패널 표시
# ======================================================
st.subheader("📊 유럽 주요 지수 현황")

eu_indices = get_eu_indices()
cols = st.columns(len(eu_indices) if len(eu_indices) > 0 else 1)

for (name, values), col in zip(eu_indices.items(), cols):
    col.metric(
        label=name,
        value=f"{values['현재가']}",
        delta=f"{values['변동률(%)']}%"
    )


# ======================================================
# 🔷 4) FastAPI 급등 종목 데이터 요청
# ======================================================
with st.spinner("실시간 데이터 불러오는 중..."):
    try:
        response = requests.get(API_URL, params={
            "interval_minutes": interval,
            "min_gain": min_gain,
            "top_n": top_n
        })
        data = response.json()

    except Exception as e:
        st.error(f"❌ 서버 연결 오류: {e}")
        data = {"results": [], "market_closed": True}


# ======================================================
# 🔷 5) 급등 종목 테이블 표시 (없어도 Streamlit 차트는 표시)
# ======================================================
if not data["market_closed"] and len(data["results"]) > 0:
    st.success("🟢 장중! 급등 종목 발견!")
    df_results = pd.DataFrame(data["results"])
    st.dataframe(df_results, use_container_width=True)
else:
    st.warning("📉 유럽 시장이 폐장했거나 조건에 맞는 종목이 없습니다.")
    st.info("그래도 아래에서 종목 차트를 확인할 수 있습니다.")


# ======================================================
# 🔷 6) 종목별 실시간 차트 (항상 표시)
# ======================================================
st.markdown("---")
st.subheader("📈 종목별 실시간 차트")

# 급등 종목이 없다면 기본 종목 리스트 제공
default_tickers = [
    "AIR.PA", "OR.PA", "MC.PA", "BNP.PA", "EN.PA", "KER.PA",
    "SIE.DE", "ALV.DE", "BMW.DE", "VOW3.DE", "AZN.L",
    "HSBA.L", "ULVR.L", "RIO.L", "NESN.SW", "UBSG.SW"
]

if len(data.get("results", [])) > 0:
    tickers = [row["티커"] for row in data["results"]]
else:
    tickers = default_tickers

selected_ticker = st.selectbox("차트를 보고 싶은 종목을 선택하세요", tickers)

if selected_ticker:
    plot_stock_chart(selected_ticker)

st.markdown("---")
st.caption("개발: 김동현 | Backend: FastAPI | Frontend: Streamlit")
