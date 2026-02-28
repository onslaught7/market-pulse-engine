import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';

const navItems = [
    { path: '/', label: 'Dashboard', icon: '◆' },
    { path: '/terminal', label: 'AI Terminal', icon: '▸' },
    { path: '/analytics', label: 'Analytics', icon: '◈' },
    { path: '/status', label: 'System Status', icon: '◉' },
];

export function Sidebar() {
    return (
        <motion.aside
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="fixed left-0 top-0 h-screen w-56 bg-bg-secondary border-r border-border flex flex-col z-50"
        >
            {/* Logo */}
            <div className="px-5 py-6 border-b border-border">
                <h1 className="text-base font-semibold tracking-tight text-text-primary">
                    Market<span className="text-accent-muted">Pulse</span>
                </h1>
                <p className="text-[10px] text-text-dim mt-0.5 tracking-widest uppercase">
                    Intelligence Engine
                </p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-3 py-4 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors duration-150 ${isActive
                                ? 'bg-accent-dim text-accent'
                                : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
                            }`
                        }
                    >
                        <span className="text-xs">{item.icon}</span>
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            {/* Footer */}
            <div className="px-5 py-4 border-t border-border">
                <p className="text-[10px] text-text-dim tracking-wide">v1.0.0 · Production</p>
            </div>
        </motion.aside>
    );
}
