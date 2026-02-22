/**
 * RunHistory Component (Frontend: Audit View)
 * ===========================================
 * 
 * Displays a paginated list of past workflow executions.
 * 
 * Responsibilities:
 * -   **Fetching**: Retrieves run data from `/system/runs`.
 * -   **Formatting**: Converts ISO timestamps to IST.
 * -   **Display**: Shows status badges (Completed/Failed).
 * -   **Details**: Opens a modal with full run details (Input/Output/Steps/UUID).
 */
import React, { useEffect, useState } from 'react';
import api from '../api';
import { Clock, ExternalLink, RefreshCw, CheckCircle, XCircle, ShieldCheck } from 'lucide-react';

const RunHistory = ({ health, onRefreshHealth }) => {
    const [runs, setRuns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastSynced, setLastSynced] = useState(new Date());

    const [selectedRun, setSelectedRun] = useState(null);

    const fetchHistory = async (isAuto = false) => {
        if (!isAuto) setLoading(true);
        setError(null);
        try {
            const res = await api.get('/runs?limit=10');
            setRuns(res.data);
            setLastSynced(new Date());
        } catch (err) {
            setError(err.message || 'Failed to fetch history');
        } finally {
            if (!isAuto) setLoading(false);
        }
    };

    const formatDateIST = (isoString) => {
        return new Date(isoString).toLocaleString('en-IN', {
            timeZone: 'Asia/Kolkata',
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    };

    useEffect(() => {
        fetchHistory();
        const interval = setInterval(() => {
            fetchHistory(true);
            if (onRefreshHealth) onRefreshHealth();
        }, 30000); // 30s auto-refresh
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            {/* Header & Sync Status */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <Clock className="w-6 h-6 text-indigo-600" />
                        Activity Hub
                    </h2>
                    <p className="text-sm text-gray-500 mt-1">Monitor system health and execution history.</p>
                </div>
                <div className="flex items-center gap-3 px-4 py-2 bg-white rounded-full border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${loading ? 'bg-indigo-500 animate-spin' : 'bg-green-500'}`}></div>
                        <span className="text-xs font-medium text-gray-600">
                            {loading ? 'Syncing...' : `Last synced ${lastSynced.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`}
                        </span>
                    </div>
                    <button
                        onClick={() => { fetchHistory(); if (onRefreshHealth) onRefreshHealth(); }}
                        className="p-1 hover:bg-gray-100 rounded-full transition-colors text-gray-400 hover:text-indigo-600"
                        title="Force Refresh"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Health Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${health?.status === 'healthy' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
                            <ShieldCheck className="w-5 h-5" />
                        </div>
                        <div>
                            <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Backend API</p>
                            <p className="text-sm font-semibold text-gray-900">{health?.status === 'healthy' ? 'Operational' : 'Unhealthy'}</p>
                        </div>
                    </div>
                    {health?.status === 'healthy' ? <CheckCircle className="w-5 h-5 text-green-500" /> : <XCircle className="w-5 h-5 text-red-500" />}
                </div>

                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${health?.database === 'connected' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
                            <ShieldCheck className="w-5 h-5" />
                        </div>
                        <div>
                            <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Database</p>
                            <p className="text-sm font-semibold text-gray-900">{health?.database === 'connected' ? 'Connected' : 'Disconnected'}</p>
                        </div>
                    </div>
                    {health?.database === 'connected' ? <CheckCircle className="w-5 h-5 text-green-500" /> : <XCircle className="w-5 h-5 text-red-500" />}
                </div>
            </div>

            {error && (
                <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
                    {error}
                </div>
            )}

            {loading && !runs.length ? (
                <div className="text-center py-12 text-gray-400">Loading history...</div>
            ) : runs.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-lg border border-gray-200 shadow-sm border-dashed">
                    <p className="text-gray-500">No runs found yet.</p>
                </div>
            ) : (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date (IST)</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Input Snippet</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pipeline</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {runs.map((run) => (
                                <tr key={run.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {formatDateIST(run.created_at)}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-900 max-w-[150px] truncate">
                                        "{run.input_text}"
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-wrap gap-1">
                                            {(run.step_runs || []).map((s, idx) => (
                                                <span key={idx} className="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-[10px] font-bold uppercase rounded border border-indigo-100">
                                                    {s.action}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                            ${run.status === 'completed' ? 'bg-green-100 text-green-800' :
                                                run.status === 'failed' ? 'bg-red-100 text-red-800' :
                                                    'bg-yellow-100 text-yellow-800'}`}>
                                            {run.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        <button
                                            onClick={() => setSelectedRun(run)}
                                            className="text-indigo-600 hover:text-indigo-900 font-medium flex items-center gap-1"
                                        >
                                            Details <ExternalLink className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Details Modal */}
            {selectedRun && (
                <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setSelectedRun(null)}>
                    <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
                        <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                            <h3 className="text-lg font-bold text-gray-900">Run Details</h3>
                            <button onClick={() => setSelectedRun(null)} className="text-gray-400 hover:text-gray-600">×</button>
                        </div>
                        <div className="p-6 overflow-y-auto space-y-4">
                            <div>
                                <h4 className="text-xs font-bold text-gray-500 uppercase mb-1">Run ID</h4>
                                <p className="font-mono text-xs text-gray-400 select-all">{selectedRun.id}</p>
                            </div>

                            <div>
                                <h4 className="text-xs font-bold text-gray-500 uppercase mb-1">Input Text</h4>
                                <p className="p-3 bg-gray-50 rounded-lg text-sm text-gray-800 whitespace-pre-wrap">{selectedRun.input_text}</p>
                            </div>

                            <div>
                                <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Step Results</h4>
                                <div className="space-y-3">
                                    {(selectedRun.step_runs || []).map((step, idx) => (
                                        <div key={idx} className="border border-gray-200 rounded-lg p-3">
                                            <div className="flex justify-between items-center mb-2">
                                                <span className="font-mono text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded">Step {step.step}: {step.action}</span>
                                            </div>
                                            <p className="text-sm text-gray-700 whitespace-pre-wrap font-mono bg-gray-50 p-2 rounded">{step.output}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                        <div className="p-4 border-t border-gray-100 bg-gray-50 flex justify-end">
                            <button
                                onClick={() => setSelectedRun(null)}
                                className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RunHistory;
