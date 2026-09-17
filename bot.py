import yfinance as yf, pandas as pd, requests, os
from datetime import datetime
print("--- NIFTY SCANNER STARTED ---", flush=True)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
print(f"TOKEN:{bool(TOKEN)} CHAT_ID:{bool(CHAT_ID)}", flush=True)

def tg(m):
    print(f"Sending: {m}", flush=True)
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m})
        print(f"Response: {r.text[:200]}", flush=True)
    except Exception as e:
        print(f"TG Error: {e}", flush=True)

tg(f"✅ NIFTY Bot LIVE {datetime.now().strftime('%H:%M %d-%m')}")

STOCKS = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS"]

for s in STOCKS:
    try:
        print(f"Checking {s}...", flush=True)
        df = yf.download(s, period="5d", interval="15m", progress=False, auto_adjust=True)
        if len(df) < 50:
            print(f"{s} no data {len(df)}", flush=True)
            continue
        close = df['Close']
        e9 = close.ewm(span=9).mean()
        e21 = close.ewm(span=21).mean()
        e50 = close.ewm(span=50).mean()
        # last closed candle
        price = float(close.iloc[-2])
        v_e9 = float(e9.iloc[-2])
        v_e21 = float(e21.iloc[-2])
        v_e50 = float(e50.iloc[-2])
        pv_e9 = float(e9.iloc[-3])
        pv_e21 = float(e21.iloc[-3])
        print(f"{s} P:{price:.1f} E9:{v_e9:.1f} E21:{v_e21:.1f} E50:{v_e50:.1f}", flush=True)
        if pv_e9 < pv_e21 and v_e9 > v_e50:
            tg(f"BUY {s.replace('.NS','')} Golden Cross Price {price:.2f}")
        elif pv_e9 > pv_e21 and v_e9 < v_e21 and v_e9 < v_e50:
            tg(f"SELL {s.replace('.NS','')} Death Cross Price {price:.2f}")
    except Exception as e:
        print(f"Error {s}: {e}", flush=True)

print("--- SCAN DONE ---", flush=True)
