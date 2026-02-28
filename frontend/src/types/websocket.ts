export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'reconnecting';

export interface TokenMessage {
    type: 'token';
    content: string;
}

export interface DoneMessage {
    type: 'done';
    sources_scanned: number;
}

export interface ErrorMessage {
    type: 'error';
    detail: string;
}

export type WSMessage = TokenMessage | DoneMessage | ErrorMessage;

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    isStreaming?: boolean;
    sourcesScanned?: number;
    timestamp: number;
}
