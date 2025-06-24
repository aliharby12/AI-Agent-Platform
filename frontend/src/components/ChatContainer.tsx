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

    try {
      // Determine file extension based on MIME type
      let extension = 'webm'; // default
      let mimeType = audioBlob.type;
      
      if (mimeType.includes('wav')) {
        extension = 'wav';
      } else if (mimeType.includes('mp3') || mimeType.includes('mpeg')) {
        extension = 'mp3';
      } else if (mimeType.includes('ogg')) {
        extension = 'ogg';
      } else if (mimeType.includes('webm')) {
        extension = 'webm';
      }

      // Create file with proper extension and MIME type
      const audioFile = new File([audioBlob], `voice-message.${extension}`, { 
        type: audioBlob.type || 'audio/webm'
      });

      const response = await sessionApi.sendVoiceMessage(selectedSession.id, audioFile, extension);
      
      // Add both user voice message and AI response to the chat
      setMessages(prev => [...prev, response.user_message, response.agent_message]);
    } catch (error: any) {
      console.error('Error sending voice message:', error);
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