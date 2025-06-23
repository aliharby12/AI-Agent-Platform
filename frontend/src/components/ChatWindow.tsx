import React from 'react';
import { ChatSession, Message } from '../services/api';

interface ChatWindowProps {
  session: ChatSession;
  messages: Message[];
  loading: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ session, messages, loading }) => (
  <div>
    {loading && <div>Loading...</div>}
    {messages.length === 0 && !loading && (
      <div style={{ color: '#888', textAlign: 'center', marginTop: 32 }}>
        No Messages here start to send and receive
      </div>
    )}
    {messages.map((msg) => (
      <div key={msg.id} style={{ marginBottom: 16, display: msg.is_user ? 'flex' : undefined, flexDirection: msg.is_user ? 'row-reverse' : undefined }}>
        <div>
          <div style={{
            background: msg.is_user ? '#2d2dff' : '#e0e0e0',
            color: msg.is_user ? '#fff' : '#000',
            borderRadius: 8,
            padding: 12,
            maxWidth: 400,
            marginBottom: 4
          }}>
            {msg?.audio_url && !msg?.is_user ? (
              <div>
                <audio
                  controls
                  style={{ width: '100%', marginBottom: 8 }}
                  onError={() => console.error('Failed to load audio')}
                  aria-label="Message audio"
                >
                  <source src={`http://localhost:8000${msg.audio_url}`} />
                  Your browser does not support the audio element.
                </audio>
                {msg.content && (
                  <div style={{ fontSize: '0.9em', opacity: 0.8 }}>
                    {msg.content}
                  </div>
                )}
              </div>
            ) : (
              msg?.content || ''
            )}
          </div>
          <div style={{ fontSize: 12, color: '#888', textAlign: msg.is_user ? 'right' : 'left' }}>
            {new Date(msg.created_at).toLocaleTimeString()}
          </div>
        </div>
      </div>
    ))}
  </div>
);

export default ChatWindow; 