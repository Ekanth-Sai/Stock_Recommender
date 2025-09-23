import React from 'react';

const IndicatorsSidebar = ({ indicators }) => {
    return (
        <div className="indicators-sidebar">
            <h3>Technical Indicators</h3>
            <ul>
                {Object.entries(indicators).map(([key, value]) => (
                    <li key={key}>
                        <strong>{key}: </strong>{value}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default IndicatorsSidebar;