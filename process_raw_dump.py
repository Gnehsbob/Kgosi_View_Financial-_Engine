import pandas as pd
import os
import zipfile
import glob
from pathlib import Path

# --- CONFIG ---
# Where the raw ZIPs are hiding
SOURCE_ROOT = "/mnt/kgosi_view_data/projects/finance/data/raw_incoming/ASCII"
# Where the clean CSVs should go
DEST_DIR = "/mnt/kgosi_view_data/projects/finance/data"

print(f"--- REFINERY STARTING ---")
print(f"Hunting for ZIPs in: {SOURCE_ROOT}")

# Recursive search for all .zip files
# This finds files even inside raw_incoming/ASCII/eurusd/2010/...
zip_files = list(Path(SOURCE_ROOT).rglob("*.zip"))

if not zip_files:
    print("No ZIP files found! Check your rsync.")
    exit()

print(f"Found {len(zip_files)} raw files. Processing...")

for zip_path in zip_files:
    try:
        filename = zip_path.name
        
        # HistData Format: HISTDATA_COM_ASCII_EURUSD_M12010.zip
        if "HISTDATA" in filename:
            # Extract Symbol
            parts = filename.split('_')
            # Usually index 3 is symbol (e.g., EURUSD)
            # HISTDATA, COM, ASCII, EURUSD, ...
            symbol = parts[3]
            
            print(f"   Processing {symbol} ({filename})...", end=" ")
            
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Find CSV inside
                target = [f for f in z.namelist() if f.endswith(".csv") or f.endswith(".txt")][0]
                
                with z.open(target) as f:
                    # Read messy format
                    df = pd.read_csv(f, sep=';', header=None)
                    df.columns = ['DateStr', 'Open', 'High', 'Low', 'Close', 'Vol']
                    
                    # Convert Date
                    df['Date'] = pd.to_datetime(df['DateStr'], format='%Y%m%d %H%M%S')
                    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Vol']]
                    
                    # Fix Timezone
                    df['Date'] = df['Date'].dt.tz_localize(None)
                    
                    # Sort
                    df.sort_values('Date', inplace=True)
                    
                    # APPEND OR CREATE
                    final_csv = os.path.join(DEST_DIR, f"{symbol}_1M.csv")
                    
                    if os.path.exists(final_csv):
                        # Merge mode
                        existing = pd.read_csv(final_csv)
                        existing['Date'] = pd.to_datetime(existing['Date'])
                        combined = pd.concat([existing, df])
                        combined.drop_duplicates(subset=['Date'], inplace=True)
                        combined.sort_values('Date', inplace=True)
                        combined.to_csv(final_csv, index=False)
                    else:
                        # Create mode
                        df.to_csv(final_csv, index=False)
                        
            print("Done")
            
    except Exception as e:
        print(f"\n Error on {filename}: {e}")

print("\n--- REFINERY FINISHED ---")
