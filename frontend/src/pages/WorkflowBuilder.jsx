/**
 * WorkflowBuilder Component (Frontend: Primary UI)
 * ================================================
 * 
 * This is the main interface for users to create and execute workflows.
 * 
 * Responsibilities:
 * -   **Configuration**: Allows users to add/remove/reorder steps.
 * -   **Input Capture**: Takes user text input.
 * -   **Execution**: Delegates to `useWorkflow` hook for API calls.
 * -   **Templates**: Provides quick-start configurations.
 */
import React, { useState } from 'react';
import { Play, Plus, Trash2, Key, Code2 } from 'lucide-react';
import StreamOutput from '../components/StreamOutput';
import { useWorkflow } from '../hooks/useWorkflow';

const PREDEFINED_TEMPLATES = {
    "quick": { label: "Quick Understanding", steps: ["clean", "summarize", "keypoints"] },
    "simplify": { label: "Simplify & Explain", steps: ["clean", "simplify", "analogy"] },
    "office": { label: "Office Assistant", steps: ["clean", "classify", "tone"] }
};

const AVAILABLE_ACTIONS = [
    { value: 'clean', label: 'Clean Text' },
    { value: 'summarize', label: 'Summarize' },
    { value: 'keypoints', label: 'Key Points' },
    { value: 'simplify', label: 'Simplify' },
    { value: 'analogy', label: 'Analogy' },
    { value: 'classify', label: 'Classify' },
    { value: 'tone', label: 'Tone Analysis' }
];

const WorkflowBuilder = ({ apiKey, setApiKey }) => {
    const [steps, setSteps] = useState([{ action: 'clean' }]);
    const [inputText, setInputText] = useState('');

    // Custom Hook for Execution Logic
    const { isRunning, status, currentStepIndex, outputLog, error, executeWorkflow } = useWorkflow();

    const addStep = () => {
        if (steps.length < 7) {
            // Find first action not currently used
            const usedActions = new Set(steps.map(s => s.action));
            const nextAction = AVAILABLE_ACTIONS.find(a => !usedActions.has(a.value))?.value || 'summarize';
            setSteps([...steps, { action: nextAction }]);
        }
    };

    const removeStep = (index) => {
        if (steps.length > 1) {
            setSteps(steps.filter((_, i) => i !== index));
        }
    };

    const updateStep = (index, action) => {
        const newSteps = [...steps];
        newSteps[index] = { action };
        setSteps(newSteps);
    };

    const loadTemplate = (templateKey) => {
        const template = PREDEFINED_TEMPLATES[templateKey];
        if (template) {
            setSteps(template.steps.map(action => ({ action })));
        }
    };

    const handleRun = () => {
        if (!inputText.trim()) return alert("Please enter some input text.");

        // Use template label if matched, otherwise generic "Custom Workflow"
        const activeTemplate = Object.values(PREDEFINED_TEMPLATES).find(
            t => JSON.stringify(t.steps) === JSON.stringify(steps.map(s => s.action))
        );
        const autoName = activeTemplate ? activeTemplate.label : "Custom Workflow";

        executeWorkflow(autoName, steps, inputText, apiKey);
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column: Configuration */}
            <div className="lg:col-span-1 space-y-6">

                {/* API Key Input */}
                <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                        <Key className="w-4 h-4 text-indigo-500" /> Groq API Key
                    </label>
                    <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="gsk_..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-mono text-sm"
                    />
                    {!apiKey && <p className="text-xs text-amber-600 mt-2">Required for execution.</p>}
                </div>

                {/* Workflow Config Wrapper */}
                <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
                    <div className="space-y-3 mb-6">
                        <label className="block text-sm font-medium text-gray-700">Steps Pipeline</label>
                        {steps.map((step, idx) => (
                            <div key={idx} className="flex gap-2 items-center">
                                <div className="bg-gray-100 text-gray-500 font-mono text-xs w-6 h-6 flex items-center justify-center rounded-full">
                                    {idx + 1}
                                </div>
                                <select
                                    value={step.action}
                                    onChange={(e) => updateStep(idx, e.target.value)}
                                    className="flex-1 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
                                >
                                    {AVAILABLE_ACTIONS.filter(opt =>
                                        // Show option if it's the current value OR if it's not used in any other step
                                        step.action === opt.value || !steps.some(s => s.action === opt.value)
                                    ).map(opt => (
                                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                                    ))}
                                </select>
                                <button
                                    onClick={() => removeStep(idx)}
                                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition"
                                    disabled={steps.length === 1}
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        ))}

                        {steps.length < 7 && (
                            <button
                                onClick={addStep}
                                className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-indigo-500 hover:text-indigo-600 transition flex items-center justify-center gap-2 text-sm font-medium"
                            >
                                <Plus className="w-4 h-4" /> Add Step
                            </button>
                        )}
                    </div>

                    {/* Templates */}
                    <div>
                        <label className="block text-xs font-medium text-gray-500 mb-2 uppercase tracking-wide">Templates</label>
                        <div className="flex flex-wrap gap-2">
                            {Object.entries(PREDEFINED_TEMPLATES).map(([key, tpl]) => (
                                <button
                                    key={key}
                                    onClick={() => loadTemplate(key)}
                                    className="px-3 py-1.5 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-full hover:bg-indigo-100 transition"
                                >
                                    {tpl.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Column: Execution */}
            <div className="lg:col-span-2 space-y-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <label className="block text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                        <Code2 className="w-4 h-4 text-indigo-500" /> Input Text
                    </label>
                    <textarea
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder="Paste your text here..."
                        className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                    />
                    <div className="mt-4 flex justify-end">
                        <button
                            onClick={handleRun}
                            disabled={isRunning || !inputText || !apiKey}
                            className={`
                           flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium text-white shadow-sm transition-colors
                           ${isRunning || !inputText || !apiKey
                                    ? 'bg-gray-400 cursor-not-allowed'
                                    : 'bg-indigo-600 hover:bg-indigo-700'}
                       `}
                        >
                            {isRunning ? 'Processing...' : (
                                <>
                                    <Play className="w-4 h-4" /> Run Workflow
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Output Area */}
                {(isRunning || status !== 'idle') && (
                    <StreamOutput
                        status={status}
                        steps={steps}
                        currentStepIndex={currentStepIndex}
                        output={outputLog}
                        error={error}
                    />
                )}
            </div>
        </div>
    );
};

export default WorkflowBuilder;
