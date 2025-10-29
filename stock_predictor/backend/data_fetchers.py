import requests
from typing import Optional, Dict
import time
import os
import finnhub 


class NSEDataFetcher:
    BASE_URL = "https://www.nseindia.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Host': 'www.nseindia.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-Requested-With': 'XMLHttpRequest',
        })
        self._refresh_session()

    def fetch_market_breadth(self) -> Optional[Dict[str, int]]:
        try:
            self._refresh_session()
            url = f"{self.BASE_URL}/api/market-data-pre-open?key=ALL"

            response = self.session.get(url, timeout = 10)

            if response.status_code != 200:
                print(f"Failed to fetch market breadth: Status {response.status_code}")
                return None 

            data = response.json()
            advances = 0
            declines = 0
            unchanged = 0

            if "data" in data:
                for index in data["data"]:
                    if "metadata" not in index:
                        continue
                    meta = index["metadata"]

                    if "advances" in meta and "declines" in meta and "unchanged" in meta:
                        advances += int(meta.get("advances", 0))
                        declines += int(meta.get("declines", 0))
                        unchanged += int(meta.get("unchanged", 0))
            
            if advances + declines + unchanged > 0:
                print(f"NSE Market Breadth: Advances = {advances}, Declines = {declines}, Unchanged = {unchanged}")

                return {
                    "advances": advances,
                    "declines": declines,
                    "unchanged": unchanged
                }
            
            print("NSE breadth data not found in response format")
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching NSE market breadth: {e}")
            return None
        except Exception as e:
            print(f"Error fetching NSE market breadth: {e}")
            return None


    def _refresh_session(self):
        try:
            base_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
            }

            # Hit homepage to refresh cookies
            homepage = f"{self.BASE_URL}/"
            resp = self.session.get(homepage, headers=base_headers, timeout=10)

            if resp.status_code == 200:
                print("NSE session refreshed successfully.")
            else:
                print(f"NSE session refresh returned {resp.status_code}")
        except Exception as e:
            print(f"Failed to refresh NSE session: {e}")

    
    def fetch_oi_pcr(self, symbol: str = "NIFTY") -> Optional[float]:
        try:
            self._refresh_session()
            url = f"{self.BASE_URL}/api/option-chain-indices?symbol={symbol}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch OI PCR: Status {response.status_code}")
                return None
            
            data = response.json()
            
            if 'records' not in data or 'data' not in data['records']:
                print("Invalid OI PCR response format")
                return None
            
            total_put_oi = 0
            total_call_oi = 0
            
            for item in data['records']['data']:
                if 'PE' in item and 'openInterest' in item['PE']:
                    total_put_oi += item['PE']['openInterest']
                if 'CE' in item and 'openInterest' in item['CE']:
                    total_call_oi += item['CE']['openInterest']
            
            if total_call_oi > 0:
                pcr = total_put_oi / total_call_oi
                print(f"Successfully fetched OI PCR for {symbol}: {pcr:.2f}")
                return pcr
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching OI PCR: {e}")
            return None
        except Exception as e:
            print(f"Error calculating OI PCR: {e}")
            return None
    

class YFinanceDataFetcher:
    @staticmethod
    def fetch_market_breadth_us() -> Optional[Dict[str, int]]:
        try:
            import yfinance as yf
    
            tickers = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM',
                'V', 'JNJ', 'WMT', 'PG', 'MA', 'HD', 'BAC', 'DIS', 'NFLX', 'CSCO'
            ]
            
            advances = 0
            declines = 0
            unchanged = 0
            
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period='2d')
                    
                    if len(hist) >= 2:
                        change = hist['Close'].iloc[-1] - hist['Close'].iloc[-2]
                        if change > 0:
                            advances += 1
                        elif change < 0:
                            declines += 1
                        else:
                            unchanged += 1
                    
                    time.sleep(0.1)  
                    
                except:
                    continue
            
            if advances > 0 or declines > 0:
                return {
                    'advances': advances,
                    'declines': declines,
                    'unchanged': unchanged
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching US market breadth: {e}")
            return None


# Stock to Index Mapping
STOCK_TO_INDEX_MAP = {
    # Indian Stocks -> NIFTY 50
    'RELIANCE.NS': '^NSEI',
    'TCS.NS': '^NSEI',
    'INFY.NS': '^NSEI',
    'HDFCBANK.NS': '^NSEI',
    'ICICIBANK.NS': '^NSEI',
    'BHARTIARTL.NS': '^NSEI',
    'SBIN.NS': '^NSEI',
    'HINDUNILVR.NS': '^NSEI',
    'ITC.NS': '^NSEI',
    'KOTAKBANK.NS': '^NSEI',
    'LT.NS': '^NSEI',
    'AXISBANK.NS': '^NSEI',
    'BAJFINANCE.NS': '^NSEI',
    'ASIANPAINT.NS': '^NSEI',
    'MARUTI.NS': '^NSEI',
    'TITAN.NS': '^NSEI',
    'ULTRACEMCO.NS': '^NSEI',
    'NESTLEIND.NS': '^NSEI',
    'WIPRO.NS': '^NSEI',
    'TECHM.NS': '^NSEI',
    'ADANIPORTS.NS': '^NSEI',
    'SUNPHARMA.NS': '^NSEI',
    'ONGC.NS': '^NSEI',
    'NTPC.NS': '^NSEI',
    'POWERGRID.NS': '^NSEI',
    'TATASTEEL.NS': '^NSEI',
    'JSWSTEEL.NS': '^NSEI',
    'HINDALCO.NS': '^NSEI',
    'COALINDIA.NS': '^NSEI',
    'INDUSINDBK.NS': '^NSEI',
    
    # Banking stocks -> NIFTY BANK
    'HDFCBANK.NS': '^NSEBANK',
    'ICICIBANK.NS': '^NSEBANK',
    'KOTAKBANK.NS': '^NSEBANK',
    'SBIN.NS': '^NSEBANK',
    'AXISBANK.NS': '^NSEBANK',
    'INDUSINDBK.NS': '^NSEBANK',
    'BANDHANBNK.NS': '^NSEBANK',
    'FEDERALBNK.NS': '^NSEBANK',
    'IDFCFIRSTB.NS': '^NSEBANK',
    'PNB.NS': '^NSEBANK',
    
    # US Stocks -> S&P 500
    'AAPL': '^GSPC',
    'MSFT': '^GSPC',
    'GOOGL': '^GSPC',
    'AMZN': '^GSPC',
    'META': '^GSPC',
    'TSLA': '^GSPC',
    'NVDA': '^GSPC',
    'JPM': '^GSPC',
    'V': '^GSPC',
    'JNJ': '^GSPC',
    'WMT': '^GSPC',
    'PG': '^GSPC',
    'MA': '^GSPC',
    'HD': '^GSPC',
    'BAC': '^GSPC',
    'DIS': '^GSPC',
    'NFLX': '^GSPC',
    'CSCO': '^GSPC',
}


_nse_fetcher = None
_yf_fetcher = None


def get_nse_fetcher() -> NSEDataFetcher:
    global _nse_fetcher
    if _nse_fetcher is None:
        _nse_fetcher = NSEDataFetcher()
    return _nse_fetcher


def get_yf_fetcher() -> YFinanceDataFetcher:
    global _yf_fetcher
    if _yf_fetcher is None:
        _yf_fetcher = YFinanceDataFetcher()
    return _yf_fetcher


def get_parent_index(ticker: str) -> Optional[str]:
    if ticker.startswith('^') or ticker in ['NIFTY_FIN_SERVICE.NS', 'NIFTY_MID_SELECT.NS']:
        return None
    
    # Return mapped index or default based on ticker suffix
    if ticker in STOCK_TO_INDEX_MAP:
        return STOCK_TO_INDEX_MAP[ticker]
    
    # Default mapping based on ticker pattern
    if ticker.endswith('.NS') or ticker.endswith('.BO'):
        return '^NSEI'  # Default to NIFTY for Indian stocks
    else:
        return '^GSPC'  # Default to S&P 500 for US stocks


def fetch_oi_pcr(ticker: str = None) -> Optional[float]:
    indian_indices = {
        '^NSEI': 'NIFTY',
        '^NSEBANK': 'BANKNIFTY',
        'NIFTY_FIN_SERVICE.NS': 'FINNIFTY',
    }
    
    if ticker in indian_indices:
        symbol = indian_indices[ticker]
        fetcher = get_nse_fetcher()
        return fetcher.fetch_oi_pcr(symbol)
    
    print(f"OI PCR not available for {ticker}")
    return None


# def fetch_market_breadth(self) -> Optional[Dict[str, int]]:
#     try:
#         self._refresh_session()
#         url = f"{self.BASE_URL}/api/market-data-pre-open?key=ALL"

#         response = self.session.get(url, timeout = 10)

#         if response.status_code != 200:
#             print(f"Failed to fetch market breadth: Status {response.status_code}")
#             return None 

#         data = response.json()
#         advances = 0
#         declines = 0
#         unchanged = 0

#         if "data" in data:
#             for index in data["data"]:
#                 if "metadata" not in index:
#                     continue
#                 meta = index["metadata"]

#                 if "advances" in meta and "declines" in meta and "unchanged" in meta:
#                     advances += int(meta.get("advances", 0))
#                     declines += int(meta.get("declines", 0))
#                     unchanged += int(meta.get("unchanged", 0))
        
#         if advances + declines + unchanged > 0:
#             print(f"NSE Market Breadth: Advances = {advances}, Declines = {declines}, Unchanged = {unchanged}")

#             return {
#                 "advances": advances,
#                 "declines": declines,
#                 "unchanged": unchanged
#             }
        
#         print("NSE breadth data not found in response format")
#         return None
    
#     except requests.exceptions.RequestException as e:
#         print(f"Network error fetching NSE market breadth: {e}")
#         return None
#     except Exception as e:
#         print(f"Error fetching NSE market breadth: {e}")
#         return None
    # if ticker and (ticker.startswith('^NSE') or ticker.endswith('.NS')):
    #     fetcher = get_nse_fetcher()
    #     return fetcher.fetch_market_breadth()
    # else:
    #     fetcher = get_yf_fetcher()
    #     return fetcher.fetch_market_breadth_us()


def fetch_market_breadth_enhanced(ticker: str = None) -> Optional[Dict[str, any]]:
    nse_fetcher = get_nse_fetcher()
    yf_fetcher = get_yf_fetcher()

    is_index = ticker and (
        ticker.startswith('^') or 
        ticker in ['NIFTY_FIN_SERVICE.NS', 'NIFTY_MID_SELECT.NS']
    )

    breadth = None

    try:
        # --- Try fetching from NSE if Indian ticker ---
        if ticker and (ticker.endswith('.NS') or ticker.startswith('^NSE')):
            breadth = nse_fetcher.fetch_market_breadth()
            if breadth:
                breadth['source'] = 'NSE API'
            else:
                print(f"⚠️ NSE fetch failed for {ticker} (401/403 likely)")

        # --- Try yfinance for global tickers ---
        elif ticker and any(x in ticker for x in ['^GSPC', 'AAPL', 'MSFT', 'GOOGL']):
            breadth = yf_fetcher.fetch_market_breadth_us()
            if breadth:
                breadth['source'] = 'Yahoo Finance'

        # --- Fallback to Finnhub if nothing worked ---
        # --- Fallback to Finnhub if nothing worked ---
        if not breadth:
            print(f"⚠️ Falling back to Finnhub for {ticker}")
            finnhub_key = os.getenv("FINNHUB_API_KEY")
            if finnhub_key:
                try:
                    client = finnhub.Client(api_key=finnhub_key)

                    # Get NIFTY 50 constituents (Finnhub symbol = ^NSEI)
                    constituents = client.index_const(symbol="^NSEI")
                    stocks = constituents.get("constituents", [])

                    advances = declines = unchanged = 0

                    for stock in stocks[:50]:  # Limit to top 50 to stay within API limits
                        try:
                            quote = client.quote(stock)
                            current_price = quote.get("c", 0)
                            prev_close = quote.get("pc", 0)

                            if current_price > prev_close:
                                advances += 1
                            elif current_price < prev_close:
                                declines += 1
                            else:
                                unchanged += 1

                            time.sleep(0.1)  # avoid rate limit (60 calls/min free tier)
                        except Exception as e:
                            continue

                    if advances + declines > 0:
                        breadth = {
                            "advances": advances,
                            "declines": declines,
                            "unchanged": unchanged,
                            "source": "Finnhub (computed)"
                        }
                        print(f"✓ Finnhub fallback breadth computed: Adv={advances}, Dec={declines}, Unch={unchanged}")
                    else:
                        print("⚠️ No breadth data available from Finnhub fallback")

                except Exception as e:
                    print(f"❌ Finnhub fallback failed: {e}")


        # --- Enrich & Return ---
        if breadth:
            if is_index:
                breadth['type'] = 'direct'
                breadth['reference_index'] = ticker
                print(f"✓ Direct breadth for {ticker} ({breadth['source']})")
            else:
                parent_index = get_parent_index(ticker)
                breadth['type'] = 'contextual'
                breadth['reference_index'] = parent_index or 'Unknown'
                breadth['ticker'] = ticker
                print(f"✓ Contextual breadth for {ticker} (via {breadth['source']})")
            return breadth

        print(f"⚠️ Could not fetch breadth for {ticker} (all sources failed)")
        return None

    except Exception as e:
        print(f"❌ Error in fetch_market_breadth_enhanced: {e}")
        return None
