import React, { useEffect, useState, useRef } from 'react';
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

  const handleSendVoiceMessage = async (audioBlob: Blob) => {
    if (!selectedSession) return;
    setLoading(true);

    // Convert Blob to File for backend compatibility
    const audioFile = new File([audioBlob], 'recording.webm', { type: audioBlob.type || 'audio/webm' });
    const formData = new FormData();
    formData.append('audio', audioFile);

    try {
      const response = await fetch(`/sessions/${selectedSession.id}/voice`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) throw new Error('Voice message failed');
      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          content: data.message.content,
          is_user: false,
          session_id: selectedSession.id,
          id: data.message.id,
          created_at: data.message.created_at,
          audio_url: data.audio_url || data.message.audio_url,
        },
      ]);
    } catch (err) {
      alert('Failed to send voice message');
    } finally {
      setLoading(false);
    }
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
            <MessageInput
              sessionId={selectedSession.id}
              onSend={handleSendMessage}
              onSendVoice={handleSendVoiceMessage}
              disabled={loading}
            />
          </>
        ) : (
          <div>Select or create a session to start chatting.</div>
        )}
      </div>
    </div>
  );
};

export default ChatContainer; 