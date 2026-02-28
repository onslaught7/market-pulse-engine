import { memo } from 'react';
import type { ConnectionState } from '../types/websocket';
import { motion } from 'framer-motion';

const stateConfig: Record<ConnectionState, { label: string; color: string; pulse: boolean }> = {
    connected: { label: 'Live', color: 'bg-status-online', pulse: true },
    connecting: { label: 'Connecting', color: 'bg-status-warning', pulse: true },
    reconnecting: { label: 'Reconnecting', color: 'bg-status-warning', pulse: true },
    disconnected: { label: 'Offline', color: 'bg-status-offline', pulse: false },
};

interface Props {
    state: ConnectionState;
}

export const ConnectionStatus = memo(function ConnectionStatus({ state }: Props) {
    const config = stateConfig[state];

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-bg-tertiary"
        >
            <span className="relative flex h-2 w-2">
                {config.pulse && (
                    <span
                        className={`absolute inline-flex h-full w-full rounded-full ${config.color} opacity-75 animate-ping`}
                    />
                )}
                <span className={`relative inline-flex h-2 w-2 rounded-full ${config.color}`} />
            </span>
            <span className="text-xs font-medium text-text-secondary tracking-wide uppercase">
                {config.label}
            </span>
        </motion.div>
    );
});
