import { useState, useCallback, useEffect } from 'react';
import { Terminal } from '../components/Terminal';
import { useWebSocket } from '../hooks/useWebSocket';
import { Topbar } from '../components/Topbar';
import type { ChatMessage, WSMessage } from '../types/websocket';

export function AITerminal() {
    const { connectionState, send, setMessageHandler } = useWebSocket();
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);

    useEffect(() => {
        setMessageHandler((msg: WSMessage) => {
            switch (msg.type) {
                case 'token':
                    setMessages((prev) => {
                        const last = prev[prev.length - 1];
                        if (last && last.role === 'assistant' && last.isStreaming) {
                            return [
                                ...prev.slice(0, -1),
                                { ...last, content: last.content + msg.content },
                            ];
                        }
                        return prev;
                    });
                    break;

                case 'done':
                    setMessages((prev) => {
                        const last = prev[prev.length - 1];
                        if (last && last.role === 'assistant') {
                            return [
                                ...prev.slice(0, -1),
                                { ...last, isStreaming: false, sourcesScanned: msg.sources_scanned },
                            ];
                        }
                        return prev;
                    });
                    setIsStreaming(false);
                    break;

                case 'error':
                    setMessages((prev) => {
                        const last = prev[prev.length - 1];
                        if (last && last.role === 'assistant' && last.isStreaming) {
                            return [
                                ...prev.slice(0, -1),
                                { ...last, content: `Error: ${msg.detail}`, isStreaming: false },
                            ];
                        }
                        return [
                            ...prev,
                            {
                                id: crypto.randomUUID(),
                                role: 'assistant',
                                content: `Error: ${msg.detail}`,
                                isStreaming: false,
                                timestamp: Date.now(),
                            },
                        ];
                    });
                    setIsStreaming(false);
                    break;
            }
        });
    }, [setMessageHandler]);

    const handleSubmit = useCallback(
        (e: React.FormEvent) => {
            e.preventDefault();
            const question = input.trim();
            if (!question || isStreaming || connectionState !== 'connected') return;

            // Add user message
            setMessages((prev) => [
                ...prev,
                {
                    id: crypto.randomUUID(),
                    role: 'user',
                    content: question,
                    timestamp: Date.now(),
                },
            ]);

            // Add empty assistant message for streaming
            setMessages((prev) => [
                ...prev,
                {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: '',
                    isStreaming: true,
                    timestamp: Date.now(),
                },
            ]);

            setIsStreaming(true);
            send({ question });
            setInput('');
        },
        [input, isStreaming, connectionState, send]
    );

    return (
        <div className="flex flex-col h-screen">
            <Topbar title="AI Terminal" connectionState={connectionState} />
            <Terminal messages={messages} />

            {/* Input Bar */}
            <div className="border-t border-border bg-bg-secondary p-4">
                <form onSubmit={handleSubmit} className="flex gap-3 max-w-4xl mx-auto">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={
                            connectionState === 'connected'
                                ? 'Ask about markets, stocks, or crypto...'
                                : 'Waiting for connection...'
                        }
                        disabled={connectionState !== 'connected' || isStreaming}
                        className="flex-1 bg-bg-tertiary border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder-text-dim focus:outline-none focus:border-accent-muted/40 focus:ring-1 focus:ring-accent-muted/20 transition-colors duration-150 disabled:opacity-50 font-mono"
                    />
                    <button
                        type="submit"
                        disabled={connectionState !== 'connected' || isStreaming || !input.trim()}
                        className="px-5 py-3 bg-accent-dim text-accent text-sm font-medium rounded-lg hover:bg-accent-muted/25 transition-colors duration-150 disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                        {isStreaming ? 'Streaming...' : 'Send'}
                    </button>
                </form>
            </div>
        </div>
    );
}
