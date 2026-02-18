import React, { useEffect, useRef } from 'react';
import { CheckCircle, Circle, Loader2, XCircle } from 'lucide-react';

const StreamOutput = ({ status, steps, currentStepIndex, output, error }) => {
    const endRef = useRef(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [output, currentStepIndex, status]);

    if (!steps) return null;

    return (
        <div className="space-y-6">
            {/* Global Loader for Sync Run */}
            {status === 'running' && (
                <div className="flex items-center justify-center p-4 bg-indigo-900/20 rounded-lg border border-indigo-900/50 mb-6 animate-pulse">
                    <Loader2 className="w-5 h-5 text-indigo-400 animate-spin mr-3" />
                    <span className="text-indigo-300 font-medium tracking-wide">
                        Processing Workflow... This may take a few moments.
                    </span>
                </div>
            )}

            {/* Progress Stepper */}
            <div className="flex items-center justify-between">
                {steps.map((step, index) => {
                    let icon = <Circle className="w-5 h-5 text-gray-300" />;
                    let color = "text-gray-400";
                    let labelColor = "text-gray-500";

                    if (index < currentStepIndex) {
                        icon = <CheckCircle className="w-5 h-5 text-green-500" />;
                        color = "text-green-500";
                        labelColor = "text-gray-900 font-medium";
                    } else if (index === currentStepIndex) {
                        if (status === 'failed') {
                            icon = <XCircle className="w-5 h-5 text-red-500" />;
                            color = "text-red-500";
                        } else if (status === 'completed') {
                            icon = <CheckCircle className="w-5 h-5 text-green-500" />;
                        } else if (status === 'running') {
                            // Keep it static/neutral during sync run as we don't know exact step
                            icon = <Circle className="w-5 h-5 text-indigo-400/50" />;
                            color = "text-indigo-400/50";
                        }
                    }

                    return (
                        <div key={index} className="flex flex-col items-center relative flex-1">
                            <div className={`mb-2 ${color}`}>
                                {icon}
                            </div>
                            <span className={`text-xs text-center ${labelColor}`}>
                                {step.action.toUpperCase()}
                            </span>
                            {index < steps.length - 1 && (
                                <div className={`hidden sm:block absolute top-2.5 left-[50%] w-full h-0.5 -z-10 
                    ${index < currentStepIndex ? 'bg-green-500' : 'bg-gray-200'}`}
                                />
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Output Display */}
            <div className="bg-gray-900 rounded-lg p-6 shadow-lg min-h-[300px] border border-gray-700">
                <div className="flex justify-between items-center mb-4 border-b border-gray-800 pb-2">
                    <h3 className="text-gray-400 text-sm font-mono">Terminal Output</h3>
                    <span className={`text-xs px-2 py-0.5 rounded ${status === 'running' ? 'bg-indigo-900 text-indigo-300' :
                        status === 'completed' ? 'bg-green-900 text-green-300' :
                            status === 'failed' ? 'bg-red-900 text-red-300' : 'bg-gray-800 text-gray-400'
                        }`}>
                        {status.toUpperCase()}
                    </span>
                </div>

                <div className="font-mono text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
                    {output && output.map((block, i) => (
                        <div key={i} className="mb-4">
                            <div className="text-indigo-400 font-bold mb-1 opacity-75">
                                [STEP {block.step}: {block.action}]
                            </div>
                            <div className="pl-4 border-l-2 border-gray-700">
                                {block.content || <span className="text-gray-600 italic">Processing...</span>}
                            </div>
                        </div>
                    ))}

                    {error && (
                        <div className="text-red-400 mt-4 p-3 bg-red-900/20 rounded border border-red-900/50">
                            Error: {error}
                        </div>
                    )}
                    <div ref={endRef} />
                </div>
            </div>
        </div>
    );
};

export default StreamOutput;
