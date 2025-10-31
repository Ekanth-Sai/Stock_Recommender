import requests
from typing import Optional, Dict
import time
import os
import finnhub 
from dhanhq import dhanhq 

import os
from typing import Optional
from dhanhq import dhanhq

class DhanDataFetcher:
    SECURITY_IDS = {
        'NIFTY': 13,        
        'BANKNIFTY': 25,    
        'FINNIFTY': 27,     
        'MIDCPNIFTY': 28,   
    }
    

    EXCHANGE_SEGMENT = dhanhq.FNO  
    
    def __init__(self):
        self.client_id = os.getenv('DHAN_CLIENT_ID')
        self.access_token = os.getenv('DHAN_ACCESS_TOKEN')
        
        if not self.client_id or not self.access_token:
            print("Warning: Dhan API credentials not found in environment variables")
            print("Set DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN to use Dhan API")
            self.dhan = None
        else:
            try:
                self.dhan = dhanhq(self.client_id, self.access_token)
                print("Dhan API client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Dhan client: {e}")
                self.dhan = None
    
    def fetch_option_chain(self, symbol: str = "NIFTY") -> Optional[dict]:
        if not self.dhan:
            print("Dhan client not initialized")
            return None
        
        symbol = symbol.upper()
        if symbol not in self.SECURITY_IDS:
            print(f"Symbol {symbol} not supported. Available: {list(self.SECURITY_IDS.keys())}")
            return None
        
        try:
            security_id = self.SECURITY_IDS[symbol]
            
            option_chain = self.dhan.get_option_chain(
                security_id=security_id,
                exchange_segment=self.EXCHANGE_SEGMENT
            )
            
            if option_chain and 'data' in option_chain:
                print(f"Successfully fetched option chain for {symbol}")
                return option_chain
            else:
                print(f"No option chain data available for {symbol}")
                return None
                
        except Exception as e:
            print(f"Error fetching option chain for {symbol}: {e}")
            return None
    
    def calculate_oi_pcr(self, symbol: str = "NIFTY") -> Optional[float]:
        option_chain = self.fetch_option_chain(symbol)
        
        if not option_chain or 'data' not in option_chain:
            return None
        
        try:
            total_put_oi = 0
            total_call_oi = 0
            
            for strike_data in option_chain['data']:
                if 'put_options' in strike_data:
                    put_oi = strike_data['put_options'].get('open_interest', 0)
                    total_put_oi += put_oi
                
                if 'call_options' in strike_data:
                    call_oi = strike_data['call_options'].get('open_interest', 0)
                    total_call_oi += call_oi
            
            if total_call_oi > 0:
                pcr = total_put_oi / total_call_oi
                print(f"OI PCR for {symbol}: {pcr:.4f}")
                print(f"  Total Put OI: {total_put_oi:,}")
                print(f"  Total Call OI: {total_call_oi:,}")
                return pcr
            else:
                print(f"No call open interest data for {symbol}")
                return None
                
        except Exception as e:
            print(f"Error calculating OI PCR for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_atm_strike_pcr(self, symbol: str = "NIFTY", spot_price: float = None) -> Optional[dict]:
        option_chain = self.fetch_option_chain(symbol)
        
        if not option_chain or 'data' not in option_chain:
            return None
        
        try:
            strikes = option_chain['data']
            
            if spot_price is None:
                mid_idx = len(strikes) // 2
                atm_range = strikes[max(0, mid_idx-2):min(len(strikes), mid_idx+3)]
            else:
                atm_range = [s for s in strikes 
                           if abs(s.get('strike_price', 0) - spot_price) <= spot_price * 0.02]
            
            atm_put_oi = 0
            atm_call_oi = 0
            
            for strike in atm_range:
                if 'put_options' in strike:
                    atm_put_oi += strike['put_options'].get('open_interest', 0)
                if 'call_options' in strike:
                    atm_call_oi += strike['call_options'].get('open_interest', 0)
            
            if atm_call_oi > 0:
                atm_pcr = atm_put_oi / atm_call_oi
                return {
                    'atm_pcr': atm_pcr,
                    'atm_put_oi': atm_put_oi,
                    'atm_call_oi': atm_call_oi,
                    'strikes_considered': len(atm_range)
                }
            
            return None
            
        except Exception as e:
            print(f"Error calculating ATM PCR: {e}")
            return None


_dhan_fetcher = None

def get_dhan_fetcher() -> DhanDataFetcher:
    global _dhan_fetcher
    if _dhan_fetcher is None:
        _dhan_fetcher = DhanDataFetcher()
    return _dhan_fetcher


def fetch_oi_pcr_dhan(ticker: str = None) -> Optional[float]:
    ticker_to_dhan = {
        '^NSEI': 'NIFTY',
        '^NSEBANK': 'BANKNIFTY',
        'NIFTY_FIN_SERVICE.NS': 'FINNIFTY',
        'NIFTY_MID_SELECT.NS': 'MIDCPNIFTY',
    }
    
    if ticker not in ticker_to_dhan:
        print(f"OI PCR not available for {ticker} via Dhan API")
        return None
    
    dhan_symbol = ticker_to_dhan[ticker]
    fetcher = get_dhan_fetcher()
    
    if not fetcher.dhan:
        print("Dhan API not available, falling back to NSE fetcher")
        return fetch_oi_pcr(ticker)
    
    return fetcher.calculate_oi_pcr(dhan_symbol)

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

STOCK_TO_INDEX_MAP = {
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
    
    if ticker in STOCK_TO_INDEX_MAP:
        return STOCK_TO_INDEX_MAP[ticker]

    if ticker.endswith('.NS') or ticker.endswith('.BO'):
        return '^NSEI'
    else:
        return '^GSPC'


def fetch_oi_pcr(ticker: str = None) -> Optional[float]:
    indian_indices = {
        '^NSEI': 'NIFTY',
        '^NSEBANK': 'BANKNIFTY',
        'NIFTY_FIN_SERVICE.NS': 'FINNIFTY',
        'NIFTY_MID_SELECT.NS': 'MIDCPNIFTY',
    }
    
    if ticker not in indian_indices:
        print(f"OI PCR not available for {ticker}")
        return None
    
    try:
        pcr = fetch_oi_pcr_dhan(ticker)
        if pcr is not None:
            return pcr
    except Exception as e:
        print(f"Dhan API failed: {e}")
    
    print("Falling back to NSE API for OI PCR")
    symbol = indian_indices[ticker]
    fetcher = get_nse_fetcher()
    return fetcher.fetch_oi_pcr(symbol)


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
        if ticker and (ticker.endswith('.NS') or ticker.startswith('^NSE')):
            breadth = nse_fetcher.fetch_market_breadth()
            if breadth:
                breadth['source'] = 'NSE API'
            else:
                print(f"NSE fetch failed for {ticker} (401/403 likely)")

        elif ticker and any(x in ticker for x in ['^GSPC', 'AAPL', 'MSFT', 'GOOGL']):
            breadth = yf_fetcher.fetch_market_breadth_us()
            if breadth:
                breadth['source'] = 'Yahoo Finance'

        if not breadth:
            print(f"Falling back to Finnhub for {ticker}")
            finnhub_key = os.getenv("FINNHUB_API_KEY")
            if finnhub_key:
                try:
                    client = finnhub.Client(api_key=finnhub_key)
                    constituents = client.index_const(symbol="^NSEI")
                    stocks = constituents.get("constituents", [])

                    advances = declines = unchanged = 0

                    for stock in stocks[:50]:  
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

                            time.sleep(0.1)  
                        except Exception as e:
                            continue

                    if advances + declines > 0:
                        breadth = {
                            "advances": advances,
                            "declines": declines,
                            "unchanged": unchanged,
                            "source": "Finnhub (computed)"
                        }
                        print(f"Finnhub fallback breadth computed: Adv={advances}, Dec={declines}, Unch={unchanged}")
                    else:
                        print("No breadth data available from Finnhub fallback")

                except Exception as e:
                    print(f"Finnhub fallback failed: {e}")

        if breadth:
            if is_index:
                breadth['type'] = 'direct'
                breadth['reference_index'] = ticker
                print(f"Direct breadth for {ticker} ({breadth['source']})")
            else:
                parent_index = get_parent_index(ticker)
                breadth['type'] = 'contextual'
                breadth['reference_index'] = parent_index or 'Unknown'
                breadth['ticker'] = ticker
                print(f"Contextual breadth for {ticker} (via {breadth['source']})")
            return breadth

        print(f"Could not fetch breadth for {ticker} (all sources failed)")
        return None

    except Exception as e:
        print(f"Error in fetch_market_breadth_enhanced: {e}")
        return None
