/**
 * useWorkflow Hook (Frontend: Business Logic)
 * ===========================================
 * 
 * Centralizes the state and API calls for executing workflows.
 * 
 * Responsibilities:
 * -   **State Management**: Tracks running status, current step, logs, and errors.
 * -   **Execution**:
 *     -   Creates workflow definition.
 *     -   Trigger sync or stream execution.
 *     -   Parses NDJSON stream updates.
 */
import { useState } from 'react';
import api from '../api';

export const useWorkflow = () => {
    const [isRunning, setIsRunning] = useState(false);
    const [status, setStatus] = useState('idle'); // idle, running, completed, failed
    const [currentStepIndex, setCurrentStepIndex] = useState(0);
    const [outputLog, setOutputLog] = useState([]);
    const [error, setError] = useState(null);

    const executeWorkflow = async (name, steps, inputText, apiKey) => {
        if (!apiKey) {
            setError("Missing API Key");
            return;
        }

        setIsRunning(true);
        setStatus('running');
        setOutputLog([]);
        setError(null);
        setCurrentStepIndex(0);

        try {
            // 1. Create Workflow Definition
            const createRes = await api.post('/workflows', {
                name,
                steps: steps
            });
            console.log("Workflow created:", createRes.data);
            const workflowId = createRes.data.id;

            // 2. Start Synchronous Run
            // Clear logs and set initial status
            setOutputLog([{ step: 0, content: "Processing workflow... Please wait.", status: "info" }]);

            const runRes = await api.post(`/workflows/${workflowId}/run`, {
                input_text: inputText
            }, {
                headers: { 'x-groq-api-key': apiKey },
                timeout: 300000 // 5 minutes timeout
            });

            const data = runRes.data;

            if (data.status === 'workflow_completed') {
                setStatus('completed');

                // Map backend steps to frontend log format
                const logs = data.steps.map(s => ({
                    step: s.step,
                    action: s.action,
                    content: s.final_output,
                    status: 'completed'
                }));
                setOutputLog(logs);
                setCurrentStepIndex(data.steps.length - 1);
            } else {
                setError("Workflow completed with unknown status");
                setStatus('failed');
            }

        } catch (err) {
            console.error("Run Workflow Error:", err);
            const errorMessage = err.response?.data?.error || err.message || "An unexpected error occurred";
            setError(errorMessage);
            setStatus('failed');
        } finally {
            setIsRunning(false);
        }
    };

    return {
        isRunning,
        status,
        currentStepIndex,
        outputLog,
        error,
        executeWorkflow
    };
};
