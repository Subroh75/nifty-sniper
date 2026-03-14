import pandas as pd
import yfinance as yf
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

def run_sniper():
    print("🚀 Initializing Nifty Sniper v1.5...")
    
    # 1. Authenticate using GitHub Secrets
    try:
        creds_json = json.loads(os.environ['GCP_SERVICE_ACCOUNT'])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        gc = gspread.authorize(creds)
        
        sheet_name = os.environ['GSHEET_NAME']
        sh = gc.open(sheet_name)
        worksheet = sh.get_worksheet(0)
        print(f"✅ Connected to Sheet: {sheet_name}")
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        return

    # 2. Define Tickers (Nifty Top 10 for initial test)
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", 
               "SBIN.NS", "INFY.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS"]

    print(f"📈 Downloading data for {len(tickers)} stocks...")
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', threads=True)

    results = []
    for ticker in tickers:
        try:
            df = data[ticker].dropna()
            if len(df) < 200: continue
            
            cp = df['Close'].iloc[-1]
            sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            std20 = df['Close'].rolling(window=20).std().iloc[-1]
            upper_band = ma20 + (std20 * 2)

            # Sniper Logic
            if cp > sma200 and cp > upper_band:
                status = "FULL BULL 🚀"
            elif cp < sma200:
                status = "BEARISH 📉"
            else:
                status = "WAITING 🕒"

            results.append([ticker, round(cp, 2), round(sma200, 2), round(upper_band, 2), status])
        except Exception as e:
            print(f"⚠️ Error processing {ticker}: {e}")

    # 3. Bulk Update Sheet
    header = ["Ticker", "Price", "200 SMA", "Upper Band", "Status"]
    worksheet.clear()
    worksheet.update('A1', [header] + results)
    print("🎯 Success! Dashboard updated.")
if __name__ == "__main__": 
    run_sniper()
