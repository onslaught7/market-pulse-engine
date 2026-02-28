import { motion } from 'framer-motion';
import { Topbar } from '../components/Topbar';

const metrics = [
    { label: 'Wisdom Collection', docs: '1,247', size: '842 MB', status: 'Indexed' },
    { label: 'Wire Collection', docs: '1,600', size: '324 MB', status: 'Live' },
];

export function Analytics() {
    return (
        <div className="flex flex-col h-screen">
            <Topbar title="Analytics" connectionState="connected" />
            <div className="flex-1 overflow-y-auto p-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
                    {metrics.map((metric, i) => (
                        <motion.div
                            key={metric.label}
                            initial={{ opacity: 0, y: 12 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.05, duration: 0.2 }}
                            className="bg-bg-secondary border border-border rounded-lg p-6"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-sm font-medium text-text-primary">{metric.label}</h3>
                                <span className="text-[10px] text-accent-muted font-mono uppercase tracking-widest">
                                    {metric.status}
                                </span>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-xs text-text-dim uppercase tracking-wider">Documents</p>
                                    <p className="text-lg font-semibold text-text-primary mt-1">{metric.docs}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-text-dim uppercase tracking-wider">Size</p>
                                    <p className="text-lg font-semibold text-text-primary mt-1">{metric.size}</p>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Embedding Model Info */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.15 }}
                    className="bg-bg-secondary border border-border rounded-lg p-6"
                >
                    <h3 className="text-xs text-text-dim uppercase tracking-wider mb-4">Model Configuration</h3>
                    <div className="space-y-3 font-mono text-xs">
                        <div className="flex justify-between text-text-secondary">
                            <span>Embedding Model</span>
                            <span className="text-text-primary">text-embedding-3-small</span>
                        </div>
                        <div className="flex justify-between text-text-secondary">
                            <span>Vector Dimensions</span>
                            <span className="text-text-primary">1536</span>
                        </div>
                        <div className="flex justify-between text-text-secondary">
                            <span>Distance Metric</span>
                            <span className="text-text-primary">Cosine</span>
                        </div>
                        <div className="flex justify-between text-text-secondary">
                            <span>LLM</span>
                            <span className="text-text-primary">GPT-4o-mini</span>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
