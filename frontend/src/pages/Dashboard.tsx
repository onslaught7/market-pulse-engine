import { motion } from 'framer-motion';
import { Topbar } from '../components/Topbar';

const stats = [
    { label: 'Documents Indexed', value: '2,847', change: '+124 today' },
    { label: 'Queries Processed', value: '1,203', change: '+89 today' },
    { label: 'Avg Response Time', value: '4.2s', change: '-0.3s' },
    { label: 'Active Sources', value: '6', change: 'All online' },
];

const recentQueries = [
    'What is the current sentiment around Bitcoin?',
    'Summarize the latest news on the S&P 500',
    'What are analysts saying about the Fed\'s interest rate decision?',
];

export function Dashboard() {
    return (
        <div className="flex flex-col h-screen">
            <Topbar title="Dashboard" connectionState="connected" />
            <div className="flex-1 overflow-y-auto p-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    {stats.map((stat, i) => (
                        <motion.div
                            key={stat.label}
                            initial={{ opacity: 0, y: 12 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.05, duration: 0.2 }}
                            className="bg-bg-secondary border border-border rounded-lg p-5"
                        >
                            <p className="text-xs text-text-dim uppercase tracking-wider">{stat.label}</p>
                            <p className="text-2xl font-semibold text-text-primary mt-2">{stat.value}</p>
                            <p className="text-xs text-accent-muted mt-1">{stat.change}</p>
                        </motion.div>
                    ))}
                </div>

                {/* Recent Activity */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="bg-bg-secondary border border-border rounded-lg p-5"
                >
                    <h3 className="text-xs text-text-dim uppercase tracking-wider mb-4">
                        Recent Queries
                    </h3>
                    <div className="space-y-3">
                        {recentQueries.map((query, i) => (
                            <div
                                key={i}
                                className="flex items-center gap-3 text-sm text-text-secondary hover:text-text-primary transition-colors duration-150 cursor-default"
                            >
                                <span className="text-accent-muted text-xs">▸</span>
                                <span className="font-mono text-xs">{query}</span>
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
