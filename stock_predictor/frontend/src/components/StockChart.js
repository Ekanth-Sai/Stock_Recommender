import React from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    BarElement,
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    BarElement
);

const StockChart = ({ chartData, historicalIndicators }) => {
    if (!historicalIndicators) {
        const singleChartData = {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Stock Price',
                    data: chartData.values,
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                },
            ],
        };
        const singleChartOptions = {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Stock Price',
                },
            },
        };
        return <Line data={singleChartData} options={singleChartOptions} />;
    }

    const { labels, close, rsi, macd, macds, macdh, bb_upper, bb_middle, bb_lower, stoch_k, stoch_d } = historicalIndicators;

    const priceChartData = {
        labels,
        datasets: [
            {
                label: 'Stock Price',
                data: close,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
            },
        ],
    };

    const priceChartOptions = {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        scales: { y: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'Price' } } },
        plugins: { title: { display: true, text: 'Stock Price' } },
    };

    const bollingerChartData = {
        labels,
        datasets: [
            {
                label: 'Bollinger Upper',
                data: bb_upper,
                borderColor: 'rgb(153, 102, 255)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                fill: '-1',
                pointRadius: 0,
            },
            {
                label: 'Bollinger Lower',
                data: bb_lower,
                borderColor: 'rgb(153, 102, 255)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                fill: '1',
                pointRadius: 0,
            },
            {
                label: 'Bollinger Middle',
                data: bb_middle,
                borderColor: 'rgb(201, 203, 207)',
                pointRadius: 0,
            },
        ],
    };

    const bollingerChartOptions = {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: { title: { display: true, text: 'Bollinger Bands' } },
    };

    const rsiChartData = {
        labels,
        datasets: [{
            label: 'RSI (14)',
            data: rsi,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            pointRadius: 0,
        }],
    };

    const rsiChartOptions = {
        responsive: true,
        scales: { y: { min: 0, max: 100, title: { display: true, text: 'RSI' } } },
        plugins: { title: { display: true, text: 'Relative Strength Index (RSI)' } },
    };

    const macdChartData = {
        labels,
        datasets: [
            {
                label: 'MACD',
                data: macd,
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                pointRadius: 0,
                type: 'line',
            },
            {
                label: 'MACD Signal',
                data: macds,
                borderColor: 'rgb(255, 206, 86)',
                backgroundColor: 'rgba(255, 206, 86, 0.5)',
                pointRadius: 0,
                type: 'line',
            },
            {
                type: 'bar',
                label: 'MACD Histogram',
                data: macdh,
                backgroundColor: 'rgba(169, 169, 169, 0.5)',
            },
        ],
    };

    const macdChartOptions = {
        responsive: true,
        plugins: { title: { display: true, text: 'MACD' } },
    };

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
        scales: { y: { min: 0, max: 100, title: { display: true, text: 'Value' } } },
        plugins: { title: { display: true, text: 'Stochastic Oscillator' } },
    };

    return (
        <div>
            <div style={{ marginBottom: '20px' }}>
                <Line data={priceChartData} options={priceChartOptions} />
            </div>
            <div style={{ marginBottom: '20px' }}>
                <Line data={bollingerChartData} options={bollingerChartOptions} />
            </div>
            <div style={{ marginBottom: '20px' }}>
                <Line data={rsiChartData} options={rsiChartOptions} />
            </div>
            <div style={{ marginBottom: '20px' }}>
                <Line data={macdChartData} options={macdChartOptions} />
            </div>
            <div style={{ marginBottom: '20px' }}>
                <Line data={stochChartData} options={stochChartOptions} />
            </div>
        </div>
    );
};

export default StockChart;