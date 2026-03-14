import pandas as pd
import yfinance as yf
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

def run_nifty_sniper():
    print("🎯 Starting Nifty Sniper Analysis...")
    
    # 1. Connect to Google Sheets
    creds_json = json.loads(os.environ['GCP_SERVICE_ACCOUNT'])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    gc = gspread.authorize(creds)
    sh = gc.open(os.environ['GSHEET_NAME'])
    wks = sh.get_worksheet(0)

    # 2. Define the Watchlist (Nifty 50 Heavyweights)
    # You can add up to 50-100 here easily
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
               "BHARTIARTL.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS"]

    results = []
    print(f"📊 Scanning {len(tickers)} stocks...")

    # 3. Data Processing
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker')

    for ticker in tickers:
        try:
            df = data[ticker].dropna()
            if len(df) < 200: continue
            
            cp = df['Close'].iloc[-1]
            sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            std20 = df['Close'].rolling(window=20).std().iloc[-1]
            upper_band = ma20 + (std20 * 2)

            # Sniper Logic: Price must be above 200 SMA AND breaking the Upper Bollinger Band
            if cp > sma200 and cp > upper_band:
                status = "🔥 FULL BULL"
            elif cp < sma200:
                status = "❄️ BEARISH"
            else:
                status = "⏳ WAITING"

            results.append([ticker, round(cp, 2), round(sma200, 2), round(upper_band, 2), status])
        except Exception as e:
            print(f"Skipping {ticker}: {e}")

    # 4. Push to Sheet
    header = ["Ticker", "Price", "200 SMA", "Upper BB", "Signal"]
    wks.clear()
    wks.update('A1', [header] + results)
    print("✅ Dashboard Updated Successfully!")

if __name__ == "__main__":
    run_nifty_sniper()
