import requests
from typing import Optional, Dict
import time


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

    def _refresh_session(self):
        try:
            self.session.get(self.BASE_URL, timeout=10)
        except requests.exceptions.RequestException as e:
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
    
    def fetch_market_breadth(self) -> Optional[Dict[str, int]]:
        try:
            self._refresh_session()
            url = f"{self.BASE_URL}/api/market-data-pre-open?key=ALL"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch market breadth: Status {response.status_code}")
                return None
            
            data = response.json()

            advances = 0
            declines = 0
            unchanged = 0
            
            if 'data' in data:
                for stock in data['data']:
                    if 'change' in stock:
                        change = stock['change']
                        if change > 0:
                            advances += 1
                        elif change < 0:
                            declines += 1
                        else:
                            unchanged += 1
            
            if advances > 0 or declines > 0:
                print(f"Market Breadth - Advances: {advances}, Declines: {declines}, Unchanged: {unchanged}")
                return {
                    'advances': advances,
                    'declines': declines,
                    'unchanged': unchanged
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching market breadth: {e}")
            return None
        except Exception as e:
            print(f"Error fetching market breadth: {e}")
            return None


class YFinanceDataFetcher:
    @staticmethod
    def fetch_market_breadth_us() -> Optional[Dict[str, int]]:
        """
        Fetch market breadth for US markets.
        Note: This is a simplified implementation.
        For production, use dedicated market data APIs.
        
        Returns:
            dict: {'advances': int, 'declines': int, 'unchanged': int} or None
        """
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


def fetch_market_breadth(ticker: str = None) -> Optional[Dict[str, int]]:
    if ticker and (ticker.startswith('^NSE') or ticker.endswith('.NS')):
        fetcher = get_nse_fetcher()
        return fetcher.fetch_market_breadth()
    else:
        fetcher = get_yf_fetcher()
        return fetcher.fetch_market_breadth_us()