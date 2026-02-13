#!/usr/bin/env python3
"""
HistData Harvester with Anti-Detection
Ethical approach: Mimics real browser behavior, respects rate limits
"""

import os
import sys
import time
import random
import zipfile
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import cloudscraper  # pip install cloudscraper
from bs4 import BeautifulSoup

# ========== CONFIG ==========
RAW_DIR = Path("/mnt/kgosi_view_data/projects/finance/data/raw")
FINAL_DIR = Path("/mnt/kgosi_view_data/projects/finance/data")

PAIRS = ["eurusd", "gbpusd", "audusd", "usdjpy", "usdchf"]
YEARS = list(range(2015, 2025))

# ========== SETUP ==========
RAW_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("histdata_robust")

# ========== ANTI-DETECTION TOOLKIT ==========

class BrowserSession:
    """Maintains a realistic browser session with human-like behavior"""
    
    def __init__(self):
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        self._warm_up()
    
    def _warm_up(self):
        """Visit homepage first to establish session cookies"""
        try:
            self.session.get('https://www.histdata.com', timeout=10)
            time.sleep(random.uniform(2.0, 4.0))
        except Exception as e:
            logger.warning(f"Warmup failed: {e}")
    
    def get_headers(self):
        """Generate realistic browser headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def human_delay(self, min_sec=3, max_sec=6):
        """Sleep with human-like timing variance"""
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"Waiting {delay:.1f}s...")
        time.sleep(delay)

# ========== DOWNLOAD LOGIC ==========

def download_histdata_year(browser, pair, year):
    """
    Download single year for a pair using token extraction
    Returns: Path to downloaded ZIP or None
    """
    pair_lower = pair.lower()
    url = 'https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes'
    
    try:
        browser.session.headers.update(browser.get_headers())
        resp = browser.session.get(url, timeout=15)
        
        if resp.status_code != 200:
            logger.error(f"[{pair} {year}] Page returned {resp.status_code}")
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        form = soup.find('form', {'id': 'file_down'})
        if not form:
            logger.error(f"[{pair} {year}]  TRAP PAGE: No form found")
            return None
        
        token_input = form.find('input', {'name': 'tk'})
        if not token_input:
            logger.error(f"[{pair} {year}]  BOT DETECTED: Token field missing entirely")
            return None
        
        token_value = token_input.get('value')
        if not token_value:
            logger.error(f"[{pair} {year}]  BOT DETECTED: Token has no value (trap page)")
            return None
        
        logger.info(f"[{pair} {year}] ✓ Token extracted: {token_value[:8]}...")
        
        browser.human_delay(4, 7)
        
        post_data = {
            'tk': token_value,
            'date': str(year),
            'dateTo': str(year),
            'platform': 'ASCII',
            'timeframe': 'M1',
            'fxpair': pair_lower.upper()
        }
        
        download_resp = browser.session.post(
            url, 
            data=post_data, 
            timeout=30,
            stream=True
        )
        
        if download_resp.status_code != 200:
            logger.error(f"[{pair} {year}] Download failed: {download_resp.status_code}")
            return None
        
        content_type = download_resp.headers.get('Content-Type', '')
        if 'zip' not in content_type and 'octet-stream' not in content_type:
            logger.error(f"[{pair} {year}] Not a ZIP file: {content_type}")
            return None
        
        zip_path = RAW_DIR / f"{pair}_{year}.zip"
        with open(zip_path, 'wb') as f:
            for chunk in download_resp.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"[{pair} {year}] Downloaded {zip_path.stat().st_size / 1024:.1f} KB")
        return zip_path
        
    except Exception as e:
        logger.error(f"[{pair} {year}] Exception: {e}")
        return None

def process_zip_to_csv(zip_path, pair, year):
    """Extract and format ZIP to standardized CSV"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            csv_name = [f for f in z.namelist() if f.endswith('.csv')][0]
            
            with z.open(csv_name) as f:
                # HistData format: YYYYMMDD HHMMSS;Open;High;Low;Close;Vol
                df = pd.read_csv(f, sep=';', header=None)
                df.columns = ['DateStr', 'Open', 'High', 'Low', 'Close', 'Volume']
                
                # Convert to datetime
                df['datetime'] = pd.to_datetime(df['DateStr'], format='%Y%m%d %H%M%S')
                df = df[['datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
                
                # Save
                output_path = FINAL_DIR / f"{pair.upper()}_1M.csv"
                
                # Append if file exists
                if output_path.exists():
                    existing = pd.read_csv(output_path)
                    existing['datetime'] = pd.to_datetime(existing['datetime'])
                    df = pd.concat([existing, df]).drop_duplicates(subset=['datetime']).sort_values('datetime')
                
                df.to_csv(output_path, index=False)
                logger.info(f"[{pair} {year}] Saved to {output_path.name}")
                
        # Cleanup ZIP
        os.remove(zip_path)
        return True
        
    except Exception as e:
        logger.error(f"[{pair} {year}] Processing failed: {e}")
        return False

# ========== MAIN ==========

def main():
    logger.info("Starting Robust HistData Harvester")
    
    browser = BrowserSession()
    
    total_success = 0
    total_failed = 0
    
    for pair in PAIRS:
        logger.info(f"\n{'='*50}\n TARGET: {pair.upper()}\n{'='*50}")
        
        for year in YEARS:
            # Check if we already have data for this year
            output_path = FINAL_DIR / f"{pair.upper()}_1M.csv"
            if output_path.exists():
                df = pd.read_csv(output_path)
                df['datetime'] = pd.to_datetime(df['datetime'])
                if any(df['datetime'].dt.year == year):
                    logger.info(f"[{pair} {year}] ⏭Already have data")
                    continue
            
            # Download
            zip_path = download_histdata_year(browser, pair, year)
            
            if zip_path:
                if process_zip_to_csv(zip_path, pair, year):
                    total_success += 1
                else:
                    total_failed += 1
            else:
                total_failed += 1
            
            browser.human_delay(5, 10)
        
        logger.info(f"Completed {pair.upper()}. Cooling down...")
        time.sleep(random.uniform(30, 60))
    
    logger.info(f"\n{'='*50}\n✅ Success: {total_success} | ❌ Failed: {total_failed}\n{'='*50}")

if __name__ == "__main__":
    main()

