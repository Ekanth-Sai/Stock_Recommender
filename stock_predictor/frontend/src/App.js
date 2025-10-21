import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import StockChart from './components/StockChart';
import IndicatorsSidebar from './components/IndicatorsSidebar';
import './App.css';

function App() {
    const [ticker, setTicker] = useState('AAPL');
    const [tickerType, setTickerType] = useState('stock'); // 'stock' or 'index'
    const [stockData, setStockData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Popular indices for quick access
    const popularIndices = [
        { symbol: '^NSEI', name: 'NIFTY 50', note: 'Indian' },
        { symbol: '^BSESN', name: 'SENSEX', note: 'Indian' },
        { symbol: '^NSEBANK', name: 'NIFTY BANK', note: 'Indian' },
        { symbol: 'NIFTY_FIN_SERVICE.NS', name: 'FINNIFTY', note: 'Indian' },
        { symbol: 'NIFTY_MID_SELECT.NS', name: 'MIDCPNIFTY', note: 'Indian' },
        { symbol: '^DJI', name: 'DOW JONES', note: 'US' },
        { symbol: '^GSPC', name: 'S&P 500', note: 'US' },
        { symbol: '^IXIC', name: 'NASDAQ', note: 'US' },
    ];
    
    const popularStocks = [
        { symbol: 'AAPL', name: 'Apple' },
        { symbol: 'GOOGL', name: 'Google' },
        { symbol: 'MSFT', name: 'Microsoft' },
        { symbol: 'RELIANCE.NS', name: 'Reliance (NSE)' },
        { symbol: 'TCS.NS', name: 'TCS (NSE)' },
        { symbol: 'INFY.NS', name: 'Infosys (NSE)' },
    ];

    const fetchData = useCallback(async () => {
        if (!ticker) return;
        setLoading(true);
        setError(null);
        try {
            // Determine if it's an index (starts with ^ or is an NSE-based index)
            const isIndex = ticker.startsWith('^') || ticker === 'NIFTYFIN.NS' || ticker === 'NIFTYMIDSELECT.NS';
            const endpoint = isIndex ? 'index' : 'stock';
            
            const response = await axios.get(`http://localhost:8000/api/${endpoint}/${ticker}`);
            setStockData(response.data);
            setTickerType(isIndex ? 'index' : 'stock');
        } catch (err) {
            const entityType = ticker.startsWith('^') || ticker === 'NIFTYFIN.NS' || ticker === 'NIFTYMIDSELECT.NS' ? 'index' : 'stock';
            setError(`Failed to fetch data for ${ticker}. Please check the ${entityType} symbol.`);
            setStockData(null);
        }
        setLoading(false);
    }, [ticker]);

    useEffect(() => {
        fetchData(); 
        const interval = setInterval(fetchData, 60000); 
        return () => clearInterval(interval); 
    }, [fetchData]);

    const handleTickerChange = (event) => {
        if (event.key === 'Enter') {
            setTicker(event.target.value.toUpperCase());
        }
    };

    const handleIndexClick = (symbol) => {
        setTicker(symbol);
    };

    return (
        <div className="App">
            <header className="header">
                <h1>Stock & Index Market Analysis</h1>
                <input
                    type="text"
                    className="ticker-input"
                    placeholder="Enter Ticker (e.g., AAPL, ^NSEI) and Press Enter"
                    defaultValue={ticker}
                    onKeyDown={handleTickerChange}
                />
                
                <div className="popular-indices">
                    <p style={{ margin: '10px 0 5px 0', fontSize: '0.9em', color: '#999' }}>
                        Quick Access:
                    </p>
                    
                    <div style={{ marginBottom: '10px' }}>
                        <span style={{ fontSize: '0.8em', color: '#888', marginRight: '10px' }}>Indices:</span>
                        <div className="index-buttons">
                            {popularIndices.map((index) => (
                                <button
                                    key={index.symbol}
                                    className={`index-button ${ticker === index.symbol ? 'active' : ''}`}
                                    onClick={() => handleIndexClick(index.symbol)}
                                    title={`${index.name} - ${index.note} Market`}
                                >
                                    {index.name}
                                </button>
                            ))}
                        </div>
                    </div>
                    
                    <div>
                        <span style={{ fontSize: '0.8em', color: '#888', marginRight: '10px' }}>Stocks:</span>
                        <div className="index-buttons">
                            {popularStocks.map((stock) => (
                                <button
                                    key={stock.symbol}
                                    className={`index-button ${ticker === stock.symbol ? 'active' : ''}`}
                                    onClick={() => handleIndexClick(stock.symbol)}
                                >
                                    {stock.name}
                                </button>
                            ))}
                        </div>
                    </div>
                    
                    {stockData && stockData.interval_type === 'daily' && (
                        <div style={{ 
                            marginTop: '10px', 
                            padding: '8px', 
                            backgroundColor: 'rgba(255, 87, 34, 0.1)', 
                            borderRadius: '4px',
                            border: '1px solid rgba(255, 87, 34, 0.3)'
                        }}>
                            <p style={{ margin: 0, fontSize: '0.85em', color: '#ff9800' }}>
                                ℹ️ Market closed - Showing daily historical data (last 30 days)
                            </p>
                        </div>
                    )}
                </div>
            </header>

            {loading && !stockData ? (
                <p>Loading initial data...</p>
            ) : error ? (
                <p className="loading-error">{error}</p>
            ) : stockData ? (
                <main className="main-content">
                    <div className="chart-container">
                        <h2>
                            {ticker} {tickerType === 'index' ? 'Index' : 'Stock'} Analysis
                            {tickerType === 'index' && (
                                <span className="index-badge">INDEX</span>
                            )}
                            {stockData.interval_type === 'daily' && (
                                <span className="index-badge" style={{backgroundColor: '#ff5722'}}>
                                    DAILY DATA
                                </span>
                            )}
                        </h2>
                        <StockChart 
                            chartData={stockData.chartData} 
                            historicalIndicators={stockData.historicalIndicators}
                            ticker={ticker}
                            tickerType={tickerType}
                            intervalType={stockData.interval_type}
                        />
                    </div>
                    <aside className="sidebar">
                        <IndicatorsSidebar 
                            indicators={stockData.prediction}
                            tickerType={tickerType}
                        />
                    </aside>
                </main>
            ) : (
                <p>Enter a ticker symbol to begin.</p>
            )}
        </div>
    );
}

export default App;