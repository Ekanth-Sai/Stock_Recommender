import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import StockChart from './components/StockChart';
import IndicatorsSidebar from './components/IndicatorsSidebar';
import './App.css';

function App() {
    const [ticker, setTicker] = useState('AAPL');
    const [stockData, setStockData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        if (!ticker) return;
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get(`http://localhost:8000/api/stock/${ticker}`);
            setStockData(response.data);
        } catch (err) {
            setError(`Failed to fetch data for ${ticker}. Please check the ticker symbol.`);
            setStockData(null);
        }
        setLoading(false);
    }, [ticker]);

    useEffect(() => {
        fetchData(); // Initial fetch
        const interval = setInterval(fetchData, 60000); 
        return () => clearInterval(interval); 
    }, [fetchData]);

    const handleTickerChange = (event) => {
        if (event.key === 'Enter') {
            setTicker(event.target.value.toUpperCase());
        }
    };

    return (
        <div className="App">
            <header className="header">
                <h1>Stock Market Analysis</h1>
                <input
                    type="text"
                    className="ticker-input"
                    placeholder="Enter Ticker (e.g., GOOGL) and Press Enter"
                    defaultValue={ticker}
                    onKeyDown={handleTickerChange}
                />
            </header>

            {loading && !stockData ? (
                <p>Loading initial data...</p>
            ) : error ? (
                <p className="loading-error">{error}</p>
            ) : stockData ? (
                <main className="main-content">
                    <div className="chart-container">
                        <h2>{ticker} Real-Time Price</h2>
                        <StockChart chartData={stockData.chartData} historicalIndicators={stockData.historicalIndicators} />
                    </div>
                    <aside className="sidebar">
                        <IndicatorsSidebar indicators={stockData.prediction} />
                    </aside>
                </main>
            ) : (
                <p>Enter a ticker symbol to begin.</p>
            )}
        </div>
    );
}

export default App;