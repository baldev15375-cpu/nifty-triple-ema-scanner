import yfinance as yf, pandas as pd, requests, os, json, time
from datetime import datetime

print("--- NIFTY SCANNER STARTED ---", flush=True)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
STATE_FILE = "last_alerts_nifty.json"

def tg(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m})
    except:
        pass

STOCKS = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS"]

try:
    with open(STATE_FILE, "r") as f:
        last_alerts = json.load(f)
except:
    last_alerts = {}

for s in STOCKS:
    try:
        df = yf.download(s, period="5d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 60:
            continue
        close = df['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:,0]
        close = close.dropna()
        e9 = close.ewm(span=9).mean()
        e21 = close.ewm(span=21).mean()
        e50 = close.ewm(span=50).mean()

        price = float(close.iloc[-1])
        ve9 = float(e9.iloc[-1])
        ve21 = float(e21.iloc[-1])
        ve50 = float(e50.iloc[-1])
        pve9 = float(e9.iloc[-2])
        pve21 = float(e21.iloc[-2])

        print(f"{s} P:{price:.1f} E9:{ve9:.1f} E21:{ve21:.1f} E50:{ve50:.1f}", flush=True)

        direction = None
        if pve9 < pve21 and ve9 > ve21 and ve21 > ve50:
            direction = "BUY"
        elif pve9 > pve21 and ve9 < ve21 and ve21 < ve50:
            direction = "SELL"

        if direction:
            last = last_alerts.get(s, {})
            last_dir = last.get("dir")
            last_time = last.get("time", 0)
            should_send = False
            if last_dir!= direction:
                should_send = True
            elif time.time() - last_time > 3600:
                should_send = True

            if should_send:
                if direction == "BUY":
                    tg(f"BUY {s.replace('.NS','')} Golden 9>21>50 Price {price:.2f}")
                else:
                    tg(f"SELL {s.replace('.NS','')} Death 9<21<50 Price {price:.2f}")
                last_alerts[s] = {"dir": direction, "time": time.time()}

    except Exception as e:
        print(f"Error {s}: {e}", flush=True)

with open(STATE_FILE, "w") as f:
    json.dump(last_alerts, f)

print("--- SCAN DONE ---", flush=True)
