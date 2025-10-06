// FILE: frontend/src/components/StockChart.js
import React from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import annotationPlugin from 'chartjs-plugin-annotation';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
    annotationPlugin
);

const StockChart = ({ chartData, historicalIndicators }) => {
    // If historical data not loaded yet
    if (!historicalIndicators) {
        const singleChartData = {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Stock Price',
                    data: chartData.values,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    fill: false,
                },
            ],
        };

        const singleChartOptions = {
            responsive: true,
            plugins: { title: { display: true, text: 'Stock Price' } },
        };

        return <Line data={singleChartData} options={singleChartOptions} />;
    }

    const {
        labels,
        close,
        rsi,
        macd,
        macds,
        macdh,
        bb_upper,
        bb_middle,
        bb_lower,
        stoch_k,
        stoch_d,
    } = historicalIndicators;

    // --- 1️⃣ Pure Stock Price Chart ---
    const priceChartData = {
        labels,
        datasets: [
            {
                label: 'Close Price',
                data: close,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.3)',
                pointRadius: 0,
            },
        ],
    };

    const priceChartOptions = {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        scales: {
            y: {
                title: { display: true, text: 'Price' },
                beginAtZero: false,
            },
        },
        plugins: { title: { display: true, text: 'Stock Price (Closing Value)' } },
    };

    // --- 2️⃣ Bollinger Bands Chart (Separate) ---
    const bollingerChartData = {
        labels,
        datasets: [
            {
                label: 'BB Upper',
                data: bb_upper,
                borderColor: 'rgba(153, 102, 255, 0.6)',
                pointRadius: 0,
            },
            {
                label: 'BB Middle',
                data: bb_middle,
                borderColor: 'rgba(201, 203, 207, 0.8)',
                borderDash: [5, 5],
                pointRadius: 0,
            },
            {
                label: 'BB Lower',
                data: bb_lower,
                borderColor: 'rgba(153, 102, 255, 0.6)',
                pointRadius: 0,
            },
        ],
    };

    const bollingerChartOptions = {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        scales: {
            y: {
                title: { display: true, text: 'Bollinger Band Value' },
                beginAtZero: false,
            },
        },
        plugins: { title: { display: true, text: 'Bollinger Bands (Volatility Range)' } },
    };

    // --- 3️⃣ RSI with horizontal 30 & 70 lines ---
    const rsiChartData = {
        labels,
        datasets: [
            {
                label: 'RSI (14)',
                data: rsi,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.4)',
                pointRadius: 0,
            },
        ],
    };

    const rsiChartOptions = {
        responsive: true,
        scales: {
            y: { min: 0, max: 100, title: { display: true, text: 'RSI' } },
        },
        plugins: {
            title: { display: true, text: 'Relative Strength Index (RSI)' },
            annotation: {
                annotations: {
                    overbought: {
                        type: 'line',
                        yMin: 70,
                        yMax: 70,
                        borderColor: 'red',
                        borderWidth: 1.5,
                        label: {
                            content: 'Overbought (70)',
                            enabled: true,
                            position: 'start',
                        },
                    },
                    oversold: {
                        type: 'line',
                        yMin: 30,
                        yMax: 30,
                        borderColor: 'green',
                        borderWidth: 1.5,
                        label: {
                            content: 'Oversold (30)',
                            enabled: true,
                            position: 'start',
                        },
                    },
                },
            },
        },
    };

    // --- 4️⃣ MACD (centered at 0 + colored histogram) ---
    const macdChartData = {
        labels,
        datasets: [
            {
                label: 'MACD',
                data: macd,
                borderColor: 'rgb(54, 162, 235)',
                pointRadius: 0,
                type: 'line',
            },
            {
                label: 'Signal',
                data: macds,
                borderColor: 'rgb(255, 206, 86)',
                pointRadius: 0,
                type: 'line',
            },
            {
                label: 'Histogram',
                data: macdh,
                backgroundColor: macdh.map((val) =>
                    val >= 0 ? 'rgba(0, 200, 0, 0.6)' : 'rgba(200, 0, 0, 0.6)'
                ),
                type: 'bar',
            },
        ],
    };

    const macdChartOptions = {
        responsive: true,
        scales: {
            y: { title: { display: true, text: 'MACD Value' }, beginAtZero: true },
        },
        plugins: {
            title: {
                display: true,
                text: 'MACD (Moving Average Convergence Divergence)',
            },
        },
    };

    // --- 5️⃣ Stochastic Oscillator with 20 & 80 lines ---
    const stochChartData = {
        labels,
        datasets: [
            {
                label: 'Stochastic %K',
                data: stoch_k,
                borderColor: 'rgb(0, 255, 0)',
                backgroundColor: 'rgba(0, 255, 0, 0.5)',
                pointRadius: 0,
            },
            {
                label: 'Stochastic %D',
                data: stoch_d,
                borderColor: 'rgb(255, 165, 0)',
                backgroundColor: 'rgba(255, 165, 0, 0.5)',
                pointRadius: 0,
            },
        ],
    };

    const stochChartOptions = {
        responsive: true,
        scales: {
            y: { min: 0, max: 100, title: { display: true, text: 'Stochastic Value' } },
        },
        plugins: {
            title: { display: true, text: 'Stochastic Oscillator' },
            annotation: {
                annotations: {
                    overbought: {
                        type: 'line',
                        yMin: 80,
                        yMax: 80,
                        borderColor: 'red',
                        borderWidth: 1.5,
                        label: {
                            content: 'Overbought (80)',
                            enabled: true,
                            position: 'start',
                        },
                    },
                    oversold: {
                        type: 'line',
                        yMin: 20,
                        yMax: 20,
                        borderColor: 'green',
                        borderWidth: 1.5,
                        label: {
                            content: 'Oversold (20)',
                            enabled: true,
                            position: 'start',
                        },
                    },
                },
            },
        },
    };

    return (
        <div>
            {/* 🔴 Live Intraday Chart */}
            {chartData && chartData.labels && chartData.labels.length > 0 && (
                <div style={{ marginBottom: '25px' }}>
                    <Line
                        data={{
                            labels: chartData.labels, // HH:MM timestamps
                            datasets: [
                                {
                                    label: 'Live Price (1-min Interval)',
                                    data: chartData.values,
                                    borderColor: 'rgba(0, 200, 255, 1)',
                                    backgroundColor: 'rgba(0, 200, 255, 0.2)',
                                    tension: 0.3,
                                    pointRadius: 0,
                                },
                            ],
                        }}
                        options={{
                            responsive: true,
                            scales: {
                                x: {
                                    title: { display: true, text: 'Time (HH:MM)' },
                                    ticks: { autoSkip: true, maxTicksLimit: 10 },
                                },
                                y: {
                                    title: { display: true, text: 'Price' },
                                    beginAtZero: false,
                                },
                            },
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Live Intraday Price (1-Min Interval)',
                                },
                                legend: { display: false },
                            },
                        }}
                    />
                </div>
            )}

            {/* 1️⃣ Stock Price */}
            <div style={{ marginBottom: '25px' }}>
                <Line data={priceChartData} options={priceChartOptions} />
            </div>

            {/* 2️⃣ Bollinger Bands */}
            <div style={{ marginBottom: '25px' }}>
                <Line data={bollingerChartData} options={bollingerChartOptions} />
            </div>

            {/* 3️⃣ RSI */}
            <div style={{ marginBottom: '25px' }}>
                <Line data={rsiChartData} options={rsiChartOptions} />
            </div>

            {/* 4️⃣ MACD */}
            <div style={{ marginBottom: '25px' }}>
                <Bar data={macdChartData} options={macdChartOptions} />
            </div>

            {/* 5️⃣ Stochastic */}
            <div style={{ marginBottom: '25px' }}>
                <Line data={stochChartData} options={stochChartOptions} />
            </div>
        </div>
    );
};

export default StockChart;
