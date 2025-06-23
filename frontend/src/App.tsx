import React from 'react';
import { AuthProvider, useAuth } from './components/AuthProvider';
import AuthPage from './components/AuthPage';
import AgentList from './components/AgentList';
import ChatHeader from './components/ChatHeader';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import './App.css';
import { Agent, ChatSession, Message, sessionApi } from './services/api';

const AppContent: React.FC = () => {
  const { isAuthenticated, loading, logout, user } = useAuth();
  const [agents, setAgents] = React.useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = React.useState<Agent | null>(null);
  const [selectedSession, setSelectedSession] = React.useState<ChatSession | null>(null);
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [chatLoading, setChatLoading] = React.useState(false);

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

  // Fetch messages when session changes
  React.useEffect(() => {
    if (selectedSession) {
      setChatLoading(true);
      sessionApi.getMessages(selectedSession.id)
        .then(setMessages)
        .catch((error: any) => {
          console.error('Error fetching messages:', error);
          if (error.response?.status === 400) {
            alert('Error loading messages. Please try again.');
          } else if (error.response?.status === 401) {
            alert('Session expired. Please login again.');
          } else {
            alert('Failed to load messages. Please check your connection.');
          }
        })
        .finally(() => setChatLoading(false));
    } else {
      setMessages([]);
    }
  }, [selectedSession]);

  // Handle sending a message
  const handleSendMessage = async (content: string) => {
    if (!selectedSession) return;
    setChatLoading(true);
    // Add user message and AI placeholder immediately
    const userMsg = {
      content,
      is_user: true,
      session_id: selectedSession.id,
      id: Date.now(),
      created_at: new Date().toISOString(),
    };
    const aiPlaceholder = {
      content: 'generating response...',
      is_user: false,
      session_id: selectedSession.id,
      id: Date.now() + 1,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMsg, aiPlaceholder]);
    try {
      const response = await sessionApi.sendMessage(selectedSession.id, content);
      setMessages(prev => {
        // Replace the last AI placeholder with the real response
        const idx = prev.findIndex(
          m => m.session_id === selectedSession.id && m.content === 'generating response...'
        );
        if (idx !== -1) {
          const newMsgs = [...prev];
          newMsgs[idx] = response;
          return newMsgs;
        }
        return prev;
      });
    } catch (error: any) {
      setMessages(prev => {
        // Replace the placeholder with an error message
        const idx = prev.findIndex(
          m => m.session_id === selectedSession.id && m.content === 'generating response...'
        );
        if (idx !== -1) {
          const newMsgs = [...prev];
          newMsgs[idx] = {
            ...aiPlaceholder,
            content: 'Failed to get response. Please try again.',
          };
          return newMsgs;
        }
        return prev;
      });
      console.error('Error sending message:', error);
      if (error.response?.status === 400) {
        alert('Invalid message. Please check your input and try again.');
      } else if (error.response?.status === 401) {
        alert('Session expired. Please login again.');
      } else if (error.response?.status === 404) {
        alert('Session not found. Please create a new chat.');
      } else {
        alert('Failed to send message. Please try again.');
      }
    } finally {
      setChatLoading(false);
    }
  };

  // Handle sending a voice message
  const handleSendVoiceMessage = async (audioBlob: Blob) => {
    if (!selectedSession) return;
    setChatLoading(true);
    try {
      // Convert Blob to File
      const extension = 'wav';
      const audioFile = new File([audioBlob], `voice-message.${extension}`, { type: audioBlob.type });
      const response = await sessionApi.sendVoiceMessage(selectedSession.id, audioFile, extension);
      setMessages(prev => [...prev, 
        { content: '[Voice Message]', is_user: true, session_id: selectedSession.id, id: Date.now(), created_at: new Date().toISOString() }, 
        response
      ]);
    } catch (error: any) {
      console.error('Error sending voice message:', error);
      if (error.response?.status === 400) {
        alert('Invalid audio format. Please try again.');
      } else if (error.response?.status === 401) {
        alert('Session expired. Please login again.');
      } else if (error.response?.status === 404) {
        alert('Session not found. Please create a new chat.');
      } else {
        alert('Failed to send voice message. Please try again.');
      }
    } finally {
      setChatLoading(false);
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
          {selectedSession ? (
            <ChatWindow session={selectedSession} messages={messages} loading={chatLoading} />
          ) : (
            <div>Select or create a session to start chatting.</div>
          )}
        </section>
        {/* Message Input */}
        <footer className="chat-footer">
          {selectedSession && (
            <MessageInput sessionId={selectedSession.id} onSend={handleSendMessage} onSendVoice={handleSendVoiceMessage} disabled={chatLoading} />
          )}
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
