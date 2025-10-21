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
                </p>
            )}
            
            {macd !== null && <p><strong>MACD:</strong> {macd}</p>}
            {macdh !== null && <p><strong>MACD Histogram:</strong> {macdh}</p>}
            {macds !== null && <p><strong>MACD Signal:</strong> {macds}</p>}
            
            <h4 style={{ marginTop: '15px', marginBottom: '10px', fontSize: '1em' }}>
                Bollinger Bands
            </h4>
            {bb_upper !== null && <p><strong>Upper Band:</strong> {bb_upper}</p>}
            {bb_middle !== null && <p><strong>Middle Band:</strong> {bb_middle}</p>}
            {bb_lower !== null && <p><strong>Lower Band:</strong> {bb_lower}</p>}
            
            <h4 style={{ marginTop: '15px', marginBottom: '10px', fontSize: '1em' }}>
                Stochastic Oscillator
            </h4>
            {stoch_k !== null && (
                <p><strong>%K:</strong> {stoch_k}
                    {stoch_k > 80 && <span style={{ color: '#f44336', marginLeft: '5px' }}>⚠ Overbought</span>}
                    {stoch_k < 20 && <span style={{ color: '#4caf50', marginLeft: '5px' }}>✓ Oversold</span>}
                </p>
            )}
            {stoch_d !== null && <p><strong>%D:</strong> {stoch_d}</p>}
        </div>
    );
};

export default IndicatorsSidebar;