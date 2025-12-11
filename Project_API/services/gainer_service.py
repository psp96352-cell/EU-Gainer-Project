import pandas as pd
from datetime import datetime
from core.config import EU_TICKERS, is_any_market_open
from data.market_loader import fetch_single_ticker

def calculate_gainers(interval_minutes: int, min_gain: float, top_n: int):
    if not is_any_market_open():
        return {
            "market_closed": True,
            "message": "현재 유럽 시장은 폐장 상태입니다.",
            "results": []
        }

    results = []
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for ticker, company in EU_TICKERS.items():
        df = fetch_single_ticker(ticker)
        if df is None or df.empty:
            continue

        df = df.dropna()
        if len(df) < interval_minutes + 2:
            continue

        try:
            # 개별 값 float 변환 (Series → float 방지)
            recent = float(df["Close"].iloc[-1])
            past = float(df["Close"].iloc[-interval_minutes - 1])
            opening = float(df["Open"].iloc[0])

            # 상승률 계산 (반드시 float 결과 보장)
            gain = ((recent - past) / past) * 100
            gain = float(gain)

        except Exception:
            # 데이터가 깨진 경우 해당 티커 건너뛰기
            continue

        # 비교도 float 기반으로 확실하게 처리
        if gain >= float(min_gain):
            results.append({
                "시간": now_str,
                "기업명": company,
                "티커": ticker,
                "당일시가": round(opening, 2),
                "현재가": round(recent, 2),
                "상승률(%)": round(gain, 2)
            })

    if len(results) == 0:
        return {
            "market_closed": False,
            "message": "장중이지만 기준에 맞는 급등 종목이 없습니다.",
            "results": []
        }

    df = pd.DataFrame(results).sort_values("상승률(%)", ascending=False).head(top_n)

    return {
        "market_closed": False,
        "message": f"{len(df)}개 종목 발견",
        "results": df.to_dict(orient="records")
    }
