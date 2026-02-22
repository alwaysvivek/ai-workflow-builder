import React, { useState } from 'react';
import Layout from './components/Layout';
import WorkflowBuilder from './pages/WorkflowBuilder';
import RunHistory from './pages/RunHistory';

function App() {
  const [activeTab, setActiveTab] = useState('builder');
  // Initialize state from local storage safely
  const [apiKey, setApiKey] = useState(import.meta.env.VITE_GROQ_API_KEY || '');
  const [health, setHealth] = useState(null);

  const checkHealth = async () => {
    try {
      const res = await api.get('/health');
      setHealth(res.data);
    } catch (err) {
      setHealth({ status: 'unhealthy', error: err.message });
    }
  };

  React.useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Global poll every 30s
    return () => clearInterval(interval);
  }, []);

  const handleApiKeyChange = (key) => {
    setApiKey(key);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'builder':
        return <WorkflowBuilder apiKey={apiKey} setApiKey={handleApiKeyChange} />;
      case 'history':
        return <RunHistory health={health} onRefreshHealth={checkHealth} />;
      default:
        return <div>Not Found</div>;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab} health={health}>
      {renderContent()}
    </Layout>
  );
}

export default App;
