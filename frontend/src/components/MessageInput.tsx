import React, { useState } from 'react';

interface MessageInputProps {
  sessionId: number | null;
  onSend: (content: string) => void;
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ sessionId, onSend, disabled }) => {
  const [value, setValue] = useState('');

  const handleSend = () => {
    if (value.trim() && sessionId) {
      onSend(value);
      setValue('');
    }
  };

  return (
    <div className="chat-input-row">
      <input
        type="text"
        value={value}
        onChange={e => setValue(e.target.value)}
        placeholder={sessionId ? 'Type your message or use voice...' : 'Select a session to chat...'}
        style={{ flex: 1, borderRadius: 4, border: '1px solid #ccc', padding: 12 }}
        disabled={!sessionId || disabled}
        onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
      />
      <button
        style={{ background: '#2d2dff', color: '#fff', border: 'none', borderRadius: 4, padding: '8px 16px' }}
        disabled={!sessionId || disabled}
        onClick={handleSend}
      >
        Send
      </button>
      <button style={{ background: '#4caf50', color: '#fff', border: 'none', borderRadius: 4, padding: '8px 16px' }} disabled={!sessionId}>Record</button>
    </div>
  );
};

export default MessageInput; 