import { memo, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import type { ChatMessage } from '../types/websocket';

interface Props {
    messages: ChatMessage[];
}

export const Terminal = memo(function Terminal({ messages }: Props) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    if (messages.length === 0) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                    <p className="text-text-dim text-sm font-mono">MarketPulse AI Terminal</p>
                    <p className="text-text-dim/50 text-xs mt-2">Ask a question about markets, stocks, or crypto</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            {messages.map((msg) => (
                <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                    className={`${msg.role === 'user' ? 'flex justify-end' : ''}`}
                >
                    {msg.role === 'user' ? (
                        <div className="max-w-xl bg-bg-elevated rounded-lg px-4 py-3 border border-border">
                            <p className="text-sm text-text-primary">{msg.content}</p>
                        </div>
                    ) : (
                        <div className="max-w-3xl">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-[10px] text-accent-muted font-mono tracking-widest uppercase">
                                    Pulse AI
                                </span>
                                {msg.sourcesScanned !== undefined && (
                                    <span className="text-[10px] text-text-dim font-mono">
                                        · {msg.sourcesScanned} sources
                                    </span>
                                )}
                            </div>
                            <div className="font-mono text-sm text-text-primary/90 leading-relaxed whitespace-pre-wrap">
                                {msg.content}
                                {msg.isStreaming && (
                                    <span className="inline-block w-1.5 h-4 bg-accent-muted ml-0.5 animate-pulse" />
                                )}
                            </div>
                        </div>
                    )}
                </motion.div>
            ))}
            <div ref={bottomRef} />
        </div>
    );
});
