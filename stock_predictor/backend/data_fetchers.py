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
    """
    Get the parent index for a stock ticker.
    Returns None if ticker is already an index or not found.
    """
    # If it's already an index, return None
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


def fetch_market_breadth(ticker: str = None) -> Optional[Dict[str, int]]:
    if ticker and (ticker.startswith('^NSE') or ticker.endswith('.NS')):
        fetcher = get_nse_fetcher()
        return fetcher.fetch_market_breadth()
    else:
        fetcher = get_yf_fetcher()
        return fetcher.fetch_market_breadth_us()


def fetch_market_breadth_enhanced(ticker: str = None) -> Optional[Dict[str, any]]:
    """
    Enhanced market breadth fetcher that handles both indices and stocks.
    
    For indices: Returns direct breadth calculation
    For stocks: Returns parent index breadth + contextual info
    
    Args:
        ticker: Stock or index ticker symbol
        
    Returns:
        dict with breadth data plus context:
        {
            'advances': int,
            'declines': int,
            'unchanged': int,
            'type': 'direct' | 'contextual',
            'reference_index': str,
            'ticker': str (only for contextual)
        }
    """
    is_index = ticker and (
        ticker.startswith('^') or 
        ticker in ['NIFTY_FIN_SERVICE.NS', 'NIFTY_MID_SELECT.NS']
    )
    
    if is_index:
        # Direct breadth calculation for indices
        breadth = fetch_market_breadth(ticker)
        if breadth:
            breadth['type'] = 'direct'
            breadth['reference_index'] = ticker
            print(f"✓ Fetched direct market breadth for index {ticker}")
        return breadth
    else:
        # For stocks, get parent index breadth
        parent_index = get_parent_index(ticker)
        if parent_index:
            breadth = fetch_market_breadth(parent_index)
            if breadth:
                breadth['type'] = 'contextual'
                breadth['reference_index'] = parent_index
                breadth['ticker'] = ticker
                print(f"✓ Fetched contextual market breadth for {ticker} from {parent_index}")
            return breadth
        return None