# NIFTY Triple EMA Scanner - FIXED with Logs
import yfinance as yf, pandas as pd, numpy as np, requests, os, json, time
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FILE = "sent.json"
STOCKS = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS"]

def load():
    try: return json.load(open(FILE))
    except: return {}
def save(d): json.dump(d, open(FILE,"w"))
def tg(m): 
    print(f"Sending Telegram: {m}")
    return requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m,"parse_mode":"Markdown"})

def adx(df):
    p=14
    df['TR']=pd.concat([df['High']-df['Low'],abs(df['High']-df['Close'].shift()),abs(df['Low']-df['Close'].shift())],axis=1).max(axis=1)
    df['+DM']=np.where((df['High']-df['High'].shift())>(df['Low'].shift()-df['Low']),np.maximum(df['High']-df['High'].shift(),0),0)
    df['-DM']=np.where((df['Low'].shift()-df['Low'])>(df['High']-df['High'].shift()),np.maximum(df['Low'].shift()-df['Low'],0),0)
    df['ATR']=df['TR'].ewm(alpha=1/p).mean()
    df['+DI']=100*(df['+DM'].ewm(alpha=1/p).mean()/df['ATR'])
    df['-DI']=100*(df['-DM'].ewm(alpha=1/p).mean()/df['ATR'])
    df['DX']=100*abs(df['+DI']-df['-DI'])/(df['+DI']+df['-DI'])
    df['ADX']=df['DX'].ewm(alpha=1/p).mean()
    return df

print("--- NIFTY SCANNER STARTED ---")
print(f"TOKEN exists: {bool(TOKEN)}, CHAT_ID exists: {bool(CHAT_ID)}")

sent=load()
# TEST MESSAGE - ਇਹ ਜ਼ਰੂਰ ਆਊਗਾ
tg(f"✅ NIFTY Scanner Started Test - {datetime.now().strftime('%H:%M %d-%m')}")

found=0
for s in STOCKS:
    try:
        print(f"Checking {s}...")
        df=yf.download(s,period="10d",interval="15m",progress=False)
        if len(df)<60: 
            print(f"{s} - Not enough data {len(df)}")
            continue
        df=adx(df)
        df['E9']=df['Close'].ewm(span=9).mean()
        df['E21']=df['Close'].ewm(span=21).mean()
        df['E50']=df['Close'].ewm(span=50).mean()
        last=df.iloc[-2]
        prev=df.iloc[-3]
        print(f"{s} - Close:{last['Close']:.1f} E9:{last['E9']:.1f} E21:{last['E21']:.1f} ADX:{last['ADX']:.1f}")

        if last['ADX']<15: continue
        golden=prev['E9']<prev['E21'] and last['E9']>last['E21'] and last['E9']>last['E50']
        death=prev['E9']>prev['E21'] and last['E9']<last['E21'] and last['E9']<last['E50']
        t=datetime.now().strftime("%H:%M %d-%m")
        if golden:
            tg(f"BUY {s.replace('.NS','')} | NIFTY Golden 9>21 Above 50 | ADX {last['ADX']:.1f} | Price {last['Close']:.2f} | {t}")
            found+=1
        elif death:
            tg(f"SELL {s.replace('.NS','')} | NIFTY Death 9<21 Below 50 | ADX {last['ADX']:.1f} | Price {last['Close']:.2f} | {t}")
            found+=1
    except Exception as e:
        print(f"Error in {s}: {e}")

print(f"--- SCAN DONE - Found {found} signals ---")
save(sent)
