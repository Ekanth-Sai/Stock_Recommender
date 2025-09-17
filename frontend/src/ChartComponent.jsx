import React from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto"; 

export default function ChartComponent({ dataPoints }) {
    const data = {
        labels: dataPoints.map(p => new Date(p.ts).toLocaleTimeString()),
        datasets: [
            {
                label: "Price",
                data: dataPoints.map(p => p.value),
                tension: 0.2,
                pointRadius: 0
            }
        ]
    };
    return <Line data={data} />;
}