import React from 'react';
import { AuthProvider, useAuth } from './components/AuthProvider';
import AuthPage from './components/AuthPage';
import AgentList from './components/AgentList';
import ChatHeader from './components/ChatHeader';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import './App.css';

const AppContent: React.FC = () => {
  const { isAuthenticated, loading, logout, user } = useAuth();

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
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar: Agent List */}
      <aside style={{ width: 300, background: '#f4f4f4', padding: 16 }}>
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
        <AgentList />
      </aside>
      {/* Main Chat Area */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#f9f9f9' }}>
        {/* Chat Header */}
        <header style={{ background: '#2d2dff', color: 'white', padding: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <ChatHeader />
          <button style={{ background: '#fff', color: '#2d2dff', border: 'none', borderRadius: 4, padding: '8px 16px', cursor: 'pointer' }}>New Chat</button>
        </header>
        {/* Chat Window */}
        <section style={{ flex: 1, padding: 24, overflowY: 'auto' }}>
          <ChatWindow />
        </section>
        {/* Message Input */}
        <footer style={{ padding: 16, background: '#fff', display: 'flex', alignItems: 'center' }}>
          <MessageInput />
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
