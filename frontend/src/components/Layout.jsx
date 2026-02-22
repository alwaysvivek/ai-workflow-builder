import React from 'react';
import { Activity, BookOpen, Clock, HeartPulse } from 'lucide-react';

const Layout = ({ children, activeTab, setActiveTab, health }) => {
    const tabs = [
        { id: 'builder', label: 'Builder', icon: Activity },
        { id: 'history', label: 'Activity', icon: Clock },
    ];

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-slate-800">
            <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="bg-indigo-600 p-2 rounded-lg">
                            <BookOpen className="w-5 h-5 text-white" />
                        </div>
                        <h1 className="text-xl font-bold text-gray-900 tracking-tight">
                            Workflow Builder
                        </h1>
                        {health && (
                            <div className="flex items-center gap-1.5 ml-4 px-2 py-1 bg-gray-50 rounded-full border border-gray-100">
                                <span className={`w-2 h-2 rounded-full ${health.status === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
                                <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">
                                    {health.status === 'healthy' ? 'Healthy' : 'Error'}
                                </span>
                            </div>
                        )}
                    </div>

                    <nav className="flex gap-1 bg-gray-100 p-1 rounded-lg overflow-x-auto">
                        {tabs.map((tab) => {
                            const Icon = tab.icon;
                            const isActive = activeTab === tab.id;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all
                    ${isActive
                                            ? 'bg-white text-indigo-600 shadow-sm'
                                            : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200/50'}
                  `}
                                >
                                    <Icon className="w-4 h-4" />
                                    {tab.label}
                                </button>
                            );
                        })}
                    </nav>
                </div>
            </header>

            <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {children}
            </main>

            <footer className="bg-white border-t border-gray-200 py-6 mt-auto">
                <div className="max-w-5xl mx-auto px-4 text-center text-sm text-gray-500">
                    <p>© {new Date().getFullYear()} Workflow Builder. Built for Better Software Assessment.</p>
                </div>
            </footer>
        </div>
    );
};

export default Layout;
