# NIFTY Triple EMA Scanner - STOCK - Separate from Crypto
import yfinance as yf, pandas as pd, numpy as np, requests, os, json, time
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FILE = "sent.json"
STOCKS = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","WIPRO.NS","SUNPHARMA.NS","TITAN.NS","HCLTECH.NS","ULTRACEMCO.NS","POWERGRID.NS","NTPC.NS"]

def load():
    try: return json.load(open(FILE))
    except: return {}
def save(d): json.dump(d, open(FILE,"w"))
def tg(m): requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m,"parse_mode":"Markdown"})

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

sent=load()
for s in STOCKS:
    try:
        df=yf.download(s,period="10d",interval="5m",progress=False)
        if len(df)<60: continue
        df=adx(df)
        df['E9']=df['Close'].ewm(span=9).mean()
        df['E21']=df['Close'].ewm(span=21).mean()
        df['E50']=df['Close'].ewm(span=50).mean()
        last,prev=df.iloc[-2],df.iloc[-3]
        if last['ADX']<20: continue
        if abs(last['E9']-last['E21'])<last['Close']*0.001: continue
        if s in sent and time.time()-sent[s]<1800: continue
        golden=prev['E9']<prev['E21'] and last['E9']>last['E21'] and last['E9']>last['E50']
        death=prev['E9']>prev['E21'] and last['E9']<last['E21'] and last['E9']<last['E50']
        t=datetime.now().strftime("%I:%M %p")
        if golden:
            tg(f"BUY {s.replace('.NS','')} | NIFTY SCANNER Golden 9>21 Above 50 | ADX {last['ADX']:.1f} | Price {last['Close']:.2f} | {t}")
            sent[s]=time.time()
        elif death:
            tg(f"SELL {s.replace('.NS','')} | NIFTY SCANNER Death 9<21 Below 50 | ADX {last['ADX']:.1f} | Price {last['Close']:.2f} | {t}")
    except: pass
save(sent)
