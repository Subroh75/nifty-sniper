import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():
    try:
        print("🔍 Checking Environment Variables...")
        if 'GCP_SERVICE_ACCOUNT' not in os.environ:
            raise ValueError("MISSING SECRET: GCP_SERVICE_ACCOUNT")
        if 'GSHEET_NAME' not in os.environ:
            raise ValueError("MISSING SECRET: GSHEET_NAME")

        print(f"📄 Connecting to Sheet: {os.environ['GSHEET_NAME']}...")
        creds_dict = json.loads(os.environ['GCP_SERVICE_ACCOUNT'])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gc = gspread.authorize(creds)
        
        sh = gc.open(os.environ['GSHEET_NAME'])
        wks = sh.get_worksheet(0)
        
        wks.update('A1', [['Connection Test Success']])
        print("✅ SUCCESS! Check your Google Sheet.")

    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        exit(1) # This tells GitHub it failed

if __name__ == "__main__":
    main()
