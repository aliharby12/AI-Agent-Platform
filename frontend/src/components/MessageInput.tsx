import React from 'react';

interface MessageInputProps {
  sessionId: number | null;
}

const MessageInput: React.FC<MessageInputProps> = ({ sessionId }) => {
  return (
    <div className="chat-input-row">
      <input type="text" placeholder={sessionId ? 'Type your message or use voice...' : 'Select a session to chat...'} style={{ flex: 1, borderRadius: 4, border: '1px solid #ccc', padding: 12 }} disabled={!sessionId} />
      <button style={{ background: '#2d2dff', color: '#fff', border: 'none', borderRadius: 4, padding: '8px 16px' }} disabled={!sessionId}>Send</button>
      <button style={{ background: '#4caf50', color: '#fff', border: 'none', borderRadius: 4, padding: '8px 16px' }} disabled={!sessionId}>Record</button>
    </div>
  );
};

export default MessageInput; 