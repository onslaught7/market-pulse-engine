import type { ConnectionState, WSMessage } from '../types/websocket';

type MessageHandler = (msg: WSMessage) => void;
type StateHandler = (state: ConnectionState) => void;

const MAX_RETRIES = 10;
const BASE_DELAY = 1000;
const MAX_DELAY = 30000;

export class WebSocketManager {
    private ws: WebSocket | null = null;
    private url: string;
    private retryCount = 0;
    private retryTimer: ReturnType<typeof setTimeout> | null = null;
    private onMessage: MessageHandler;
    private onStateChange: StateHandler;
    private intentionalClose = false;

    constructor(url: string, onMessage: MessageHandler, onStateChange: StateHandler) {
        this.url = url;
        this.onMessage = onMessage;
        this.onStateChange = onStateChange;
    }

    connect(): void {
        this.intentionalClose = false;
        this.onStateChange(this.retryCount > 0 ? 'reconnecting' : 'connecting');

        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                this.retryCount = 0;
                this.onStateChange('connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const msg: WSMessage = JSON.parse(event.data);
                    this.onMessage(msg);
                } catch {
                    // Ignore malformed messages
                }
            };

            this.ws.onclose = () => {
                if (!this.intentionalClose) {
                    this.onStateChange('disconnected');
                    this.scheduleReconnect();
                }
            };

            this.ws.onerror = () => {
                // onclose will fire after onerror — reconnect logic lives there
            };
        } catch {
            this.onStateChange('disconnected');
            this.scheduleReconnect();
        }
    }

    private scheduleReconnect(): void {
        if (this.retryCount >= MAX_RETRIES || this.intentionalClose) return;

        const delay = Math.min(BASE_DELAY * Math.pow(2, this.retryCount), MAX_DELAY);
        this.retryCount++;

        this.onStateChange('reconnecting');
        this.retryTimer = setTimeout(() => this.connect(), delay);
    }

    send(data: Record<string, unknown>): void {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    disconnect(): void {
        this.intentionalClose = true;
        if (this.retryTimer) clearTimeout(this.retryTimer);
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.onStateChange('disconnected');
    }
}
