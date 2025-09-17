import { io } from "socket.io-client";

export function connectWS(ticker) {
    const url = `ws://localhost:8000/ws/realtime/${encodeURIComponent(ticker)}`;
    const ws = new WebSocket(url);

    return ws;
}

