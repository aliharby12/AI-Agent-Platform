import React, { useEffect, useState } from 'react';
import { sessionApi, ChatSession, Message } from '../services/api';
import ChatWindow from './ChatWindow';
import MessageInput from './MessageInput';

interface ChatContainerProps {
  token: string;
  agentId: number;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ token, agentId }) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    sessionApi.listSessions().then(setSessions);
  }, []);

  useEffect(() => {
    if (selectedSession) {
      setLoading(true);
      sessionApi.getMessages(selectedSession.id)
        .then(setMessages)
        .finally(() => setLoading(false));
    } else {
      setMessages([]);
    }
  }, [selectedSession]);

  const handleNewSession = async () => {
    const session = await sessionApi.createSession(agentId);
    setSessions([...sessions, session]);
    setSelectedSession(session);
  };

  const handleSendMessage = async (content: string) => {
    if (!selectedSession) return;
    setLoading(true);
    const response = await sessionApi.sendMessage(selectedSession.id, content);
    setMessages((prev) => [...prev, { content, is_user: true, session_id: selectedSession.id, id: Date.now(), created_at: new Date().toISOString() }, response]);
    setLoading(false);
  };

  const handleDeleteSession = async (sessionId: number) => {
    await sessionApi.deleteSession(sessionId);
    setSessions(sessions.filter(s => s.id !== sessionId));
    if (selectedSession?.id === sessionId) setSelectedSession(null);
  };

  return (
    <div>
      <div>
        <button onClick={handleNewSession}>New Chat</button>
        <ul>
          {sessions.map(session => (
            <li key={session.id}>
              <button onClick={() => setSelectedSession(session)}>
                Session {session.id}
              </button>
              <button onClick={() => handleDeleteSession(session.id)}>Delete</button>
            </li>
          ))}
        </ul>
      </div>
      <div>
        {selectedSession ? (
          <>
            <ChatWindow session={selectedSession} messages={messages} loading={loading} />
            <MessageInput sessionId={selectedSession.id} onSend={handleSendMessage} disabled={loading} />
          </>
        ) : (
          <div>Select or create a session to start chatting.</div>
        )}
      </div>
    </div>
  );
};

export default ChatContainer; 