import React, { useEffect, useState } from 'react';
import api from '../api';
import { CheckCircle, XCircle, RefreshCcw } from 'lucide-react';

const StatusPage = () => {
    const [health, setHealth] = useState(null);
    const [loading, setLoading] = useState(true);

    const checkHealth = async () => {
        setLoading(true);
        try {
            const res = await api.get('/health');
            setHealth(res.data);
        } catch (err) {
            setHealth({ status: 'unhealthy', error: err.message });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkHealth();
        const interval = setInterval(checkHealth, 30000); // Poll every 30s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">System Status</h2>
                    <button
                        onClick={checkHealth}
                        className="p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors"
                        disabled={loading}
                    >
                        <RefreshCcw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">Backend API</span>
                        {health?.status === 'healthy' ? (
                            <span className="flex items-center text-green-600 gap-2 text-sm font-medium">
                                <CheckCircle className="w-5 h-5" /> Operational
                            </span>
                        ) : (
                            <span className="flex items-center text-red-600 gap-2 text-sm font-medium">
                                <XCircle className="w-5 h-5" /> {health?.error || 'Unavailable'}
                            </span>
                        )}
                    </div>

                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">Database (SQLite)</span>
                        {health?.database === 'connected' ? (
                            <span className="flex items-center text-green-600 gap-2 text-sm font-medium">
                                <CheckCircle className="w-5 h-5" /> Connected
                            </span>
                        ) : (
                            <span className="flex items-center text-red-600 gap-2 text-sm font-medium">
                                <XCircle className="w-5 h-5" /> {health?.database || 'Disconnected'}
                            </span>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StatusPage;
