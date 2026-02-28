import { motion } from 'framer-motion';
import { Topbar } from '../components/Topbar';

interface ServiceInfo {
    name: string;
    container: string;
    port: string;
    language: string;
    status: 'online' | 'offline' | 'degraded';
}

const services: ServiceInfo[] = [
    { name: 'Redis', container: 'vortex-redis', port: '6379', language: 'C', status: 'online' },
    { name: 'Qdrant', container: 'vortex-qdrant', port: '6333', language: 'Rust', status: 'online' },
    { name: 'Gateway', container: 'vortex-gateway', port: '8080', language: 'Go', status: 'online' },
    { name: 'Worker', container: 'vortex-worker', port: '—', language: 'Python', status: 'online' },
    { name: 'Producer', container: 'vortex-producer', port: '—', language: 'Go', status: 'online' },
    { name: 'API', container: 'vortex-api', port: '8000', language: 'Python', status: 'online' },
];

const statusColors = {
    online: 'bg-status-online',
    degraded: 'bg-status-warning',
    offline: 'bg-status-error',
};

export function SystemStatus() {
    return (
        <div className="flex flex-col h-screen">
            <Topbar title="System Status" connectionState="connected" />
            <div className="flex-1 overflow-y-auto p-6">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="bg-bg-secondary border border-border rounded-lg overflow-hidden"
                >
                    <div className="px-5 py-4 border-b border-border">
                        <h3 className="text-xs text-text-dim uppercase tracking-wider">
                            Service Health — 6 Containers
                        </h3>
                    </div>

                    <div className="divide-y divide-border">
                        {services.map((svc, i) => (
                            <motion.div
                                key={svc.name}
                                initial={{ opacity: 0, x: -8 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.04, duration: 0.15 }}
                                className="flex items-center justify-between px-5 py-4 hover:bg-bg-hover transition-colors duration-150"
                            >
                                <div className="flex items-center gap-3">
                                    <span className="relative flex h-2 w-2">
                                        {svc.status === 'online' && (
                                            <span className={`absolute inline-flex h-full w-full rounded-full ${statusColors[svc.status]} opacity-75 animate-ping`} />
                                        )}
                                        <span className={`relative inline-flex h-2 w-2 rounded-full ${statusColors[svc.status]}`} />
                                    </span>
                                    <div>
                                        <p className="text-sm font-medium text-text-primary">{svc.name}</p>
                                        <p className="text-xs text-text-dim font-mono">{svc.container}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-6">
                                    <span className="text-xs text-text-secondary font-mono w-16 text-right">
                                        {svc.port}
                                    </span>
                                    <span className="text-xs text-text-dim w-14 text-right">{svc.language}</span>
                                    <span className="text-[10px] text-accent-muted uppercase tracking-widest w-12 text-right">
                                        {svc.status}
                                    </span>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>

                {/* Architecture Overview */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="mt-4 bg-bg-secondary border border-border rounded-lg p-5"
                >
                    <h3 className="text-xs text-text-dim uppercase tracking-wider mb-3">Data Flow</h3>
                    <p className="font-mono text-xs text-text-secondary leading-relaxed">
                        Producer → Gateway → Redis → Worker → Qdrant ← API ← Frontend
                    </p>
                </motion.div>
            </div>
        </div>
    );
}
