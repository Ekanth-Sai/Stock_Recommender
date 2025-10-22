import React, { useState } from 'react';
import './IndicatorsSidebar.css';

const IndicatorsSidebar = ({ indicators, tickerType }) => {
    const [expandedIndicator, setExpandedIndicator] = useState(null);

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
        detailed_analyses,
        signal_summary
    } = indicators;

    const toggleIndicator = (indicatorName) => {
        setExpandedIndicator(expandedIndicator === indicatorName ? null : indicatorName);
    };

    const getSignalColor = (signal) => {
        const colors = {
            'bullish': '#4caf50',
            'bearish': '#f44336',
            'overbought': '#ff9800',
            'oversold': '#2196f3',
            'neutral': '#9e9e9e'
        };
        return colors[signal] || '#9e9e9e';
    };

    const getSignalIcon = (signal) => {
        const icons = {
            'bullish': '📈',
            'bearish': '📉',
            'overbought': '⚠️',
            'oversold': '💡',
            'neutral': '➖'
        };
        return icons[signal] || '❓';
    };

    const renderIndicatorCard = (title, value, analysis, additionalInfo = null) => {
        if (!analysis) return null;

        const isExpanded = expandedIndicator === title;

        return (
            <div className="indicator-card" key={title}>
                <div 
                    className="indicator-header"
                    onClick={() => toggleIndicator(title)}
                    style={{ cursor: 'pointer' }}
                >
                    <div className="indicator-title-row">
                        <h4>{title}</h4>
                        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                    </div>
                    <div className="indicator-value-row">
                        <span className="indicator-value">{value}</span>
                        <span 
                            className="signal-badge"
                            style={{ backgroundColor: getSignalColor(analysis.signal) }}
                        >
                            {getSignalIcon(analysis.signal)} {analysis.signal.toUpperCase()}
                        </span>
                    </div>
                    <div className="strength-bar-container">
                        <div 
                            className="strength-bar"
                            style={{ 
                                width: `${analysis.strength * 100}%`,
                                backgroundColor: getSignalColor(analysis.signal)
                            }}
                        />
                    </div>
                    <span className="strength-label">
                        Signal Strength: {(analysis.strength * 100).toFixed(0)}%
                    </span>
                </div>

                {isExpanded && (
                    <div className="indicator-details">
                        {additionalInfo && (
                            <div className="additional-info">
                                {additionalInfo}
                            </div>
                        )}
                        
                        <div className="explanation-section">
                            <h5>📊 Analysis</h5>
                            <p className="explanation-text">{analysis.explanation}</p>
                        </div>

                        {analysis.recommendations && analysis.recommendations.length > 0 && (
                            <div className="recommendations-section">
                                <h5>💡 Recommendations</h5>
                                <ul className="recommendations-list">
                                    {analysis.recommendations.map((rec, idx) => (
                                        <li key={idx}>{rec}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="indicators-sidebar">
            <h3>
                {tickerType === 'index' ? 'Index Analysis' : 'Stock Analysis'}
            </h3>
            
            {/* Overall Recommendation */}
            <div className="overall-recommendation">
                <div className="recommendation-header">
                    <h4>Overall Recommendation</h4>
                </div>
                {action && (
                    <div className="recommendation-content">
                        <div className="action-display">
                            <span className={`action-${action.toLowerCase()}`}>
                                {action === 'Buy' ? '🟢' : action === 'Sell' ? '🔴' : '🟡'} {action}
                            </span>
                        </div>
                        {confidence !== null && (
                            <div className="confidence-display">
                                <span className="confidence-label">Confidence:</span>
                                <div className="confidence-bar-container">
                                    <div 
                                        className="confidence-bar"
                                        style={{ width: `${confidence * 100}%` }}
                                    />
                                </div>
                                <span className="confidence-value">
                                    {(confidence * 100).toFixed(2)}%
                                </span>
                            </div>
                        )}
                        
                        {signal_summary && (
                            <div className="signal-summary">
                                <div className="summary-item">
                                    <span className="summary-icon" style={{ color: '#4caf50' }}>📈</span>
                                    <span>Bullish: {signal_summary.bullish_signals}</span>
                                </div>
                                <div className="summary-item">
                                    <span className="summary-icon" style={{ color: '#f44336' }}>📉</span>
                                    <span>Bearish: {signal_summary.bearish_signals}</span>
                                </div>
                                <div className="summary-item">
                                    <span className="summary-icon" style={{ color: '#ff9800' }}>⚠️</span>
                                    <span>Overbought: {signal_summary.overbought_signals}</span>
                                </div>
                                <div className="summary-item">
                                    <span className="summary-icon" style={{ color: '#2196f3' }}>💡</span>
                                    <span>Oversold: {signal_summary.oversold_signals}</span>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="indicators-list">
                <h4 className="section-title">Technical Indicators</h4>
                <p className="section-subtitle">Click on any indicator for detailed analysis</p>

                {/* RSI */}
                {rsi !== null && detailed_analyses?.rsi && renderIndicatorCard(
                    'RSI (14)',
                    rsi,
                    detailed_analyses.rsi,
                    <div className="rsi-zones">
                        <div className="zone-indicator">
                            <span className={rsi > 70 ? 'zone-active' : ''}>Overbought {'>'}70</span>
                            <span className={rsi >= 30 && rsi <= 70 ? 'zone-active' : ''}>Neutral 30-70</span>
                            <span className={rsi < 30 ? 'zone-active' : ''}>Oversold {'<'}30</span>
                        </div>
                    </div>
                )}

                {/* MACD */}
                {macd !== null && detailed_analyses?.macd && renderIndicatorCard(
                    'MACD',
                    `${macd} / ${macds}`,
                    detailed_analyses.macd,
                    <div className="macd-details">
                        <div className="macd-row">
                            <span>MACD Line:</span>
                            <strong>{macd}</strong>
                        </div>
                        <div className="macd-row">
                            <span>Signal Line:</span>
                            <strong>{macds}</strong>
                        </div>
                        <div className="macd-row">
                            <span>Histogram:</span>
                            <strong style={{ color: macdh >= 0 ? '#4caf50' : '#f44336' }}>
                                {macdh}
                            </strong>
                        </div>
                    </div>
                )}

                {/* Bollinger Bands */}
                {bb_middle !== null && detailed_analyses?.bollinger_bands && renderIndicatorCard(
                    'Bollinger Bands',
                    bb_middle,
                    detailed_analyses.bollinger_bands,
                    <div className="bb-details">
                        <div className="bb-row">
                            <span>Upper Band:</span>
                            <strong>{bb_upper}</strong>
                        </div>
                        <div className="bb-row">
                            <span>Middle Band:</span>
                            <strong>{bb_middle}</strong>
                        </div>
                        <div className="bb-row">
                            <span>Lower Band:</span>
                            <strong>{bb_lower}</strong>
                        </div>
                        <div className="bb-row">
                            <span>Band Width:</span>
                            <strong>{((bb_upper - bb_lower) / bb_middle * 100).toFixed(2)}%</strong>
                        </div>
                    </div>
                )}

                {/* Stochastic Oscillator */}
                {stoch_k !== null && detailed_analyses?.stochastic && renderIndicatorCard(
                    'Stochastic Oscillator',
                    `%K: ${stoch_k}`,
                    detailed_analyses.stochastic,
                    <div className="stoch-details">
                        <div className="stoch-row">
                            <span>%K (Fast):</span>
                            <strong>{stoch_k}</strong>
                        </div>
                        <div className="stoch-row">
                            <span>%D (Slow):</span>
                            <strong>{stoch_d}</strong>
                        </div>
                        <div className="zone-indicator">
                            <span className={stoch_k > 80 ? 'zone-active' : ''}>Overbought {'>'}80</span>
                            <span className={stoch_k >= 20 && stoch_k <= 80 ? 'zone-active' : ''}>Neutral 20-80</span>
                            <span className={stoch_k < 20 ? 'zone-active' : ''}>Oversold {'<'}20</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Fallback for old data format without detailed_analyses */}
            {!detailed_analyses && (
                <div className="legacy-indicators">
                    <h4 style={{ marginTop: '20px', marginBottom: '10px', fontSize: '1em' }}>
                        Technical Indicators (Legacy View)
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
            )}
        </div>
    );
};

export default IndicatorsSidebar;