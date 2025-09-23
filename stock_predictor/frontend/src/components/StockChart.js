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
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const StockChart = ({ chartData, historicalIndicators }) => {
    const datasets = [
        {
            label: 'Stock Price',
            data: chartData.values,
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            yAxisID: 'y',
        },
    ];

    if (historicalIndicators) {
        // RSI
        datasets.push({
            label: 'RSI (14)',
            data: historicalIndicators.rsi,
            fill: false,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            yAxisID: 'y1',
            pointRadius: 0,
        });

        // MACD
        datasets.push({
            label: 'MACD',
            data: historicalIndicators.macd,
            fill: false,
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            yAxisID: 'y1',
            pointRadius: 0,
        });
        datasets.push({
            label: 'MACD Signal',
            data: historicalIndicators.macds,
            fill: false,
            borderColor: 'rgb(255, 206, 86)',
            backgroundColor: 'rgba(255, 206, 86, 0.5)',
            yAxisID: 'y1',
            pointRadius: 0,
        });

        // Bollinger Bands
        datasets.push({
            label: 'Bollinger Upper',
            data: historicalIndicators.bb_upper,
            fill: false,
            borderColor: 'rgb(153, 102, 255)',
            backgroundColor: 'rgba(153, 102, 255, 0.5)',
            yAxisID: 'y',
            pointRadius: 0,
        });
        datasets.push({
            label: 'Bollinger Middle',
            data: historicalIndicators.bb_middle,
            fill: false,
            borderColor: 'rgb(201, 203, 207)',
            backgroundColor: 'rgba(201, 203, 207, 0.5)',
            yAxisID: 'y',
            pointRadius: 0,
        });
        datasets.push({
            label: 'Bollinger Lower',
            data: historicalIndicators.bb_lower,
            fill: false,
            borderColor: 'rgb(153, 102, 255)',
            backgroundColor: 'rgba(153, 102, 255, 0.5)',
            yAxisID: 'y',
            pointRadius: 0,
        });

        // Stochastic Oscillator
        datasets.push({
            label: 'Stochastic %K',
            data: historicalIndicators.stoch_k,
            fill: false,
            borderColor: 'rgb(0, 255, 0)',
            backgroundColor: 'rgba(0, 255, 0, 0.5)',
            yAxisID: 'y1',
            pointRadius: 0,
        });
        datasets.push({
            label: 'Stochastic %D',
            data: historicalIndicators.stoch_d,
            fill: false,
            borderColor: 'rgb(255, 165, 0)',
            backgroundColor: 'rgba(255, 165, 0, 0.5)',
            yAxisID: 'y1',
            pointRadius: 0,
        });
    }

    const data = {
        labels: historicalIndicators ? historicalIndicators.labels : chartData.labels,
        datasets: datasets,
    };

    const options = {
        responsive: true,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        stacked: false,
        scales: {
            y: {
                type: 'linear',
                display: true,
                position: 'left',
                title: {
                    display: true,
                    text: 'Price',
                },
            },
            y1: {
                type: 'linear',
                display: true,
                position: 'right',
                grid: {
                    drawOnChartArea: false,
                },
                title: {
                    display: true,
                    text: 'Indicator Value',
                },
                min: 0,
                max: 100,
            },
        },
    };

    return <Line data={data} options={options} />;
};

export default StockChart;
