import React, { useEffect, useState, useRef } from "react";
import ChartComponent from "./ChartComponent";
import { connectWS } from "./socket";

function App() {
    const [ticker, setTicker] = useState("INFY.NS");
    const [dataPoints, setDataPoints] = useState([]);
    const [prediction, setPrediction] = useState(null);
    const wsRef = useRef(null);

    useEffect(() => {
    wsRef.current = connectWS(ticker);
    const ws = wsRef.current;
        ws.onopen = () => console.log("WS opened");
        
    ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    const ts = msg.timestamp;
    const price = msg.close;
    setDataPoints(prev => {
        const next = [...prev, { ts, value: price }];
        return next.slice(-200); 
    });
    setPrediction({ pred: msg.prediction, conf: msg.confidence, probs: msg.probs });
    };
    ws.onclose = () => console.log("WS closed");
    return () => {
        if (ws) ws.close();
    };
    }, [ticker]);

    return (
    <div style={{ padding: 20 }}>
        <h2>Live Stock Recommender ({ticker})</h2>
        <div style={{ width: "800px", height: "400px" }}>
            <ChartComponent dataPoints={dataPoints} />
        </div>
        <div style={{ marginTop: 20 }}>
            <h3>Recommendation</h3>
            {prediction ? (
            <div>
                <strong>{prediction.pred}</strong> (conf: {(prediction.conf*100).toFixed(1)}%)
                <pre>{JSON.stringify(prediction.probs, null, 2)}</pre>
            </div>
        ) : <div>No prediction yet</div>}
        </div>
    </div>
    );
}

export default App;
