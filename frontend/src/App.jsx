import React, { useState } from 'react';
import Layout from './components/Layout';
import WorkflowBuilder from './pages/WorkflowBuilder';
import RunHistory from './pages/RunHistory';
import StatusPage from './pages/StatusPage';

function App() {
  const [activeTab, setActiveTab] = useState('builder');
  // Initialize state from local storage safely
  const [apiKey, setApiKey] = useState(import.meta.env.VITE_GROQ_API_KEY || '');

  const handleApiKeyChange = (key) => {
    setApiKey(key);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'builder':
        return <WorkflowBuilder apiKey={apiKey} setApiKey={handleApiKeyChange} />;
      case 'history':
        return <RunHistory />;
      case 'status':
        return <StatusPage />;
      default:
        return <div>Not Found</div>;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </Layout>
  );
}

export default App;
