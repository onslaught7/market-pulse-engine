import { ConnectionStatus } from './ConnectionStatus';
import type { ConnectionState } from '../types/websocket';

interface Props {
    title: string;
    connectionState: ConnectionState;
}

export function Topbar({ title, connectionState }: Props) {
    return (
        <header className="h-14 border-b border-border bg-bg-secondary/80 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-40">
            <h2 className="text-sm font-medium text-text-primary tracking-tight">{title}</h2>
            <ConnectionStatus state={connectionState} />
        </header>
    );
}
