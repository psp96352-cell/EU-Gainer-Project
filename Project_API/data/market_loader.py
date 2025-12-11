import yfinance as yf
import time

def fetch_single_ticker(ticker: str, retries: int = 6):
    for _ in range(retries):
        try:
            df = yf.download(ticker, period="1d", interval="1m", progress=False)
            if df is not None and not df.empty:
                return df
            time.sleep(0.4)
        except:
            time.sleep(0.4)
    return None
