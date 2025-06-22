import React from 'react';
import { AuthProvider, useAuth } from './components/AuthProvider';
import AuthPage from './components/AuthPage';
import AgentList from './components/AgentList';
import ChatHeader from './components/ChatHeader';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import './App.css';
import { Agent, ChatSession } from './services/api';

const AppContent: React.FC = () => {
  const { isAuthenticated, loading, logout, user } = useAuth();
  const [agents, setAgents] = React.useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = React.useState<Agent | null>(null);
  const [selectedSession, setSelectedSession] = React.useState<ChatSession | null>(null);

  // Handler to update agent list and selected agent
  const handleAgentListUpdate = (newAgents: Agent[]) => {
    setAgents(newAgents);
    if (newAgents.length === 0) {
      setSelectedAgent(null);
      setSelectedSession(null);
    } else if (!selectedAgent || !newAgents.some(a => a.id === selectedAgent.id)) {
      setSelectedAgent(newAgents[0]);
      setSelectedSession(null);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  return (
    <div className="app-layout">
      {/* Sidebar: Agent List */}
      <aside className="sidebar">
        <div style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontWeight: 'bold' }}>Welcome, {user?.username}!</span>
            <button 
              onClick={logout}
              style={{ 
                background: '#dc3545', 
                color: 'white', 
                border: 'none', 
                borderRadius: 4, 
                padding: '4px 8px', 
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Logout
            </button>
          </div>
        </div>
        <AgentList
          onSelectAgent={agent => {
            setSelectedAgent(agent);
            setSelectedSession(null);
          }}
          onAgentListUpdate={handleAgentListUpdate}
        />
      </aside>
      {/* Main Chat Area */}
      <main className="chat-main">
        {/* Chat Header */}
        <header className="chat-header">
          <ChatHeader
            selectedAgent={selectedAgent}
            selectedSession={selectedSession}
            onSelectSession={setSelectedSession}
            agents={agents}
          />
        </header>
        {/* Chat Window */}
        <section className="chat-window-section">
          <ChatWindow session={selectedSession} />
        </section>
        {/* Message Input */}
        <footer className="chat-footer">
          <MessageInput sessionId={selectedSession?.id ?? null} />
        </footer>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
