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

tg(f"✅ NIFTY Bot LIVE {datetime.now().strftime('%H:%M %d-%m-%y')}")

STOCKS = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS"]

for s in STOCKS:
    try:
        print(f"Checking {s}...", flush=True)
        df = yf.download(s, period="5d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 60:
            print(f"{s} no data {len(df)}", flush=True)
            continue
        # Fix for new yfinance - flatten Close
        close = df['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:,0]
        close = close.dropna()
        
        e9 = close.ewm(span=9).mean()
        e21 = close.ewm(span=21).mean()
        e50 = close.ewm(span=50).mean()
        
        price = float(close.iloc[-2])
        ve9 = float(e9.iloc[-2])
        ve21 = float(e21.iloc[-2])
        ve50 = float(e50.iloc[-2])
        pve9 = float(e9.iloc[-3])
        pve21 = float(e21.iloc[-3])
        
        print(f"{s} P:{price:.1f} E9:{ve9:.1f} E21:{ve21:.1f} E50:{ve50:.1f}", flush=True)
        
        if pve9 < pve21 and ve9 > ve21 and ve9 > ve50:
            tg(f"🟢 BUY {s.replace('.NS','')} Golden 9>21>50 Price {price:.2f}")
        elif pve9 > pve21 and ve9 < ve21 and ve9 < ve50:
            tg(f"🔴 SELL {s.replace('.NS','')} Death 9<21<50 Price {price:.2f}")
            
    except Exception as e:
        print(f"Error {s}: {e}", flush=True)
        import traceback
        traceback.print_exc()

print("--- SCAN DONE ---", flush=True)
