import React from 'react';

const IndicatorsSidebar = ({ indicators, tickerType }) => {
    if (!indicators) {
        return <div>Loading...</div>
    }

    const {
        action,
        confidence,
        rsi,
        macd,
        macdh,
        macds,
        bb_lower,
        bb_middle,
        bb_upper,
        stoch_k,
        stoch_d,
    } = indicators;

    return (
        <div className="indicators-sidebar">
            <h3>
                {tickerType === 'index' ? 'Index Analysis' : 'Stock Analysis'}
            </h3>
            
            <div style={{ 
                marginBottom: '15px', 
                padding: '10px', 
                backgroundColor: 'rgba(74, 144, 226, 0.1)',
                borderRadius: '5px',
                borderLeft: '3px solid #4a90e2'
            }}>
                {action && (
                    <p style={{ margin: '5px 0' }}>
                        <strong>Recommendation: </strong>
                        <span className={`action-${action.toLowerCase()}`}>
                            {action}
                        </span>
                    </p>
                )}
                {confidence !== null && (
                    <p style={{ margin: '5px 0' }}>
                        <strong>Confidence: </strong>
                        {(confidence * 100).toFixed(2)}%
                    </p>
                )}
            </div>

            <h4 style={{ marginTop: '20px', marginBottom: '10px', fontSize: '1em' }}>
                Technical Indicators
            </h4>
            
            {rsi !== null && (
                <p><strong>RSI (14):</strong> {rsi}
                    {rsi > 70 && <span style={{ color: '#f44336', marginLeft: '5px' }}>⚠ Overbought</span>}
                    {rsi < 30 && <span style={{ color: '#4caf50', marginLeft: '5px' }}>✓ Oversold</span>}
                    {rsi > 70 && <p className="indicator-explanation">RSI indicates overbought conditions, suggesting a potential reversal or pullback.</p>}
                    {rsi < 30 && <p className="indicator-explanation">RSI indicates oversold conditions, suggesting a potential bounce or reversal.</p>}
                    {rsi >= 30 && rsi <= 70 && <p className="indicator-explanation">RSI is in the neutral zone, indicating no strong overbought or oversold signals.</p>}
                </p>
            )}
            
            {macd !== null && <p><strong>MACD:</strong> {macd}</p>}
            {macdh !== null && <p><strong>MACD Histogram:</strong> {macdh}</p>}
            {macds !== null && <p><strong>MACD Signal:</strong> {macds}</p>}
            {(macd !== null && macds !== null && macdh !== null) && (
                <p className="indicator-explanation">
                    {macd > macds && macdh > 0 && "MACD shows a bullish crossover and positive histogram, indicating upward momentum."}
                    {macd < macds && macdh < 0 && "MACD shows a bearish crossover and negative histogram, indicating downward momentum."}
                    {Math.abs(macd - macds) < 0.1 && Math.abs(macdh) < 0.1 && "MACD is flat, suggesting weak momentum or consolidation."}
                </p>
            )}
            
            <h4 style={{ marginTop: '15px', marginBottom: '10px', fontSize: '1em' }}>
                Bollinger Bands
            </h4>
            {bb_upper !== null && <p><strong>Upper Band:</strong> {bb_upper}</p>}
            {bb_middle !== null && <p><strong>Middle Band:</strong> {bb_middle}</p>}
            {bb_lower !== null && <p><strong>Lower Band:</strong> {bb_lower}</p>}
            {(bb_upper !== null && bb_lower !== null) && (
                <p className="indicator-explanation">
                    {bb_upper - bb_lower > bb_middle * 0.1 && "Bollinger Bands are wide, indicating high volatility."}
                    {bb_upper - bb_lower < bb_middle * 0.05 && "Bollinger Bands are narrow, indicating low volatility and potential for a breakout."}
                </p>
            )}
            
            <h4 style={{ marginTop: '15px', marginBottom: '10px', fontSize: '1em' }}>
                Stochastic Oscillator
            </h4>
            {stoch_k !== null && (
                <p><strong>%K:</strong> {stoch_k}
                    {stoch_k > 80 && <span style={{ color: '#f44336', marginLeft: '5px' }}>⚠ Overbought</span>}
                    {stoch_k < 20 && <span style={{ color: '#4caf50', marginLeft: '5px' }}>✓ Oversold</span>}
                    {stoch_k > 80 && stoch_d > 80 && <p className="indicator-explanation">Stochastic Oscillator indicates overbought conditions, suggesting a potential reversal.</p>}
                    {stoch_k < 20 && stoch_d < 20 && <p className="indicator-explanation">Stochastic Oscillator indicates oversold conditions, suggesting a potential bounce.</p>}
                </p>
            )}
            {stoch_d !== null && <p><strong>%D:</strong> {stoch_d}</p>}
        </div>
    );
};

export default IndicatorsSidebar;