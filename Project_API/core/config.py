import pytz
from datetime import datetime

EU_TICKERS = {
    "AIR.PA": "Airbus",
    "OR.PA": "L’Oréal",
    "MC.PA": "LVMH",
    "BNP.PA": "BNP Paribas",
    "KER.PA": "Kering",
    "SIE.DE": "Siemens",
    "ALV.DE": "Allianz",
    "BMW.DE": "BMW",
    "VOW3.DE": "Volkswagen",
    "AZN.L": "AstraZeneca",
    "HSBA.L": "HSBC",
    "ULVR.L": "Unilever",
    "RIO.L": "Rio Tinto",
    "NESN.SW": "Nestlé",
    "UBSG.SW": "UBS Group"
}

MARKET_INFO = {
    "PA": {"open": 9, "close": 17.5, "timezone": "Europe/Paris"},
    "DE": {"open": 9, "close": 17.5, "timezone": "Europe/Berlin"},
    "L":  {"open": 8, "close": 16.5, "timezone": "Europe/London"},
    "SW": {"open": 9, "close": 17.5, "timezone": "Europe/Zurich"},
}

def is_any_market_open():
    for info in MARKET_INFO.values():
        tz = pytz.timezone(info["timezone"])
        now_local = datetime.now(tz)
        hour_now = now_local.hour + now_local.minute / 60
        if info["open"] <= hour_now <= info["close"]:
            return True
    return False
