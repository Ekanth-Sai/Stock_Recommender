import React from 'react';

const Prediction = ({ prediction }) => {
    if (!prediction) {
        return <div>Loading Prediction...</div>
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
    } = prediction; 

    return (
        <div className="prediction">
            <h3>Prediction</h3>
            <p><strong>Action: </strong>{action}</p>
            <p><strong>Confidence: </strong>{(confidence * 100).toFixed(2)}%</p>
            {rsi !== null && <p><strong>RSI (14):</strong>{rsi}</p>}
            {macd !== null && <p><strong>MACD:</strong>{macd}</p>}
            {macdh !== null && <p><strong>MACD Histogram:</strong>{macdh}</p>}
            {macds !== null && <p><strong>MACD Signal:</strong>{macds}</p>}
            {bb_upper !== null && <p><strong>Bollinger Upper:</strong>{bb_upper}</p>}
            {bb_middle !== null && <p><strong>Bollinger Middle:</strong>{bb_middle}</p>}
            {bb_lower !== null && <p><strong>Bollinger Lower:</strong>{bb_lower}</p>}
            {stoch_k !== null && <p><strong>Stochastic K:</strong>{stoch_k}</p>}
            {stoch_d !== null && <p><strong>Stochastic D:</strong>{stoch_d}</p>}
        </div>
    );
};

export default Prediction;