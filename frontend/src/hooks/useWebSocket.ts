import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketManager } from '../lib/websocket';
import type { ConnectionState, WSMessage } from '../types/websocket';

const WS_URL = `ws://${window.location.hostname}:8000/ws`;

export function useWebSocket() {
    const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
    const managerRef = useRef<WebSocketManager | null>(null);
    const handlersRef = useRef<((msg: WSMessage) => void) | null>(null);

    const setMessageHandler = useCallback((handler: (msg: WSMessage) => void) => {
        handlersRef.current = handler;
    }, []);

    useEffect(() => {
        const manager = new WebSocketManager(
            WS_URL,
            (msg) => handlersRef.current?.(msg),
            setConnectionState
        );
        managerRef.current = manager;
        manager.connect();

        return () => manager.disconnect();
    }, []);

    const send = useCallback((data: Record<string, unknown>) => {
        managerRef.current?.send(data);
    }, []);

    return { connectionState, send, setMessageHandler };
}
