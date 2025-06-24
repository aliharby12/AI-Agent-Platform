import React from 'react';
import { ChatSession, Message } from '../services/api';

interface ChatWindowProps {
  session: ChatSession;
  messages: Message[];
  loading: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ session, messages, loading }) => {
  // Debug logging for audio URLs
  React.useEffect(() => {
    messages.forEach((msg, index) => {
      if (msg.audio_url) {
        console.log(`Message ${index} (${msg.is_user ? 'user' : 'agent'}):`, {
          id: msg.id,
          audio_url: msg.audio_url,
          full_url: `http://localhost:8000${msg.audio_url}`,
          content: msg.content
        });
      }
    });
  }, [messages]);

  return (
    <div>
      {loading && <div>Loading...</div>}
      {messages.length === 0 && !loading && (
        <div style={{ color: '#888', textAlign: 'center', marginTop: 32 }}>
          No Messages here start to send and receive
        </div>
      )}
      {messages.map((msg) => (
        <div
          key={msg.id}
          style={{
            marginBottom: 16,
            display: 'flex',
            flexDirection: msg.is_user ? 'row-reverse' : 'row',
            alignItems: 'flex-end',
          }}
        >
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.is_user ? 'flex-end' : 'flex-start',
              width: '100%',
            }}
          >
            <div
              style={{
                background: msg.is_user ? '#2d2dff' : '#e0e0e0',
                color: msg.is_user ? '#fff' : '#000',
                borderRadius: 12,
                padding: 12,
                minWidth: 220,
                maxWidth: 400,
                marginBottom: 4,
                marginRight: msg.is_user ? 16 : 0,
                marginLeft: !msg.is_user ? 16 : 0,
                boxShadow: '0 2px 8px rgba(0,0,0,0.07)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: msg.is_user ? 'flex-end' : 'flex-start',
                alignSelf: msg.is_user ? 'flex-end' : 'flex-start',
              }}
            >
              {msg?.audio_url ? (
                <audio
                  controls
                  style={{
                    width: '100%',
                    marginBottom: 8,
                    background: 'transparent',
                    outline: 'none',
                  }}
                  onError={(e) => {
                    console.error('Failed to load audio:', {
                      audio_url: msg.audio_url,
                      full_url: `http://localhost:8000${msg.audio_url}`,
                      error: e
                    });
                  }}
                  onLoadStart={() => {
                    console.log('Loading audio:', {
                      audio_url: msg.audio_url,
                      full_url: `http://localhost:8000${msg.audio_url}`
                    });
                  }}
                  aria-label="Message audio"
                >
                  <source src={`http://localhost:8000${msg.audio_url}`} />
                  Your browser does not support the audio element.
                </audio>
              ) : (
                msg?.content || ''
              )}
            </div>
            <div
              style={{
                fontSize: 12,
                color: '#888',
                textAlign: msg.is_user ? 'right' : 'left',
                width: '100%',
                marginRight: msg.is_user ? 16 : 0,
                marginLeft: !msg.is_user ? 16 : 0,
              }}
            >
              {new Date(msg.created_at).toLocaleTimeString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChatWindow; 