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

  const buttonStyle = {
    border: 'none',
    borderRadius: 4,
    padding: '8px 16px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  };

  const sendButtonStyle = {
    ...buttonStyle,
    background: '#2d2dff',
    color: '#fff',
  };

  const recordButtonStyle = {
    ...buttonStyle,
    background: '#4caf50',
    color: '#fff',
  };

  const disabledButtonStyle = {
    ...buttonStyle,
    background: '#ccc',
    color: '#666',
    cursor: 'not-allowed',
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
        style={disabled ? disabledButtonStyle : sendButtonStyle}
        disabled={!sessionId || disabled}
        onClick={handleSend}
        onMouseEnter={(e) => {
          if (!disabled && sessionId) {
            e.currentTarget.style.background = '#1a1aff';
            e.currentTarget.style.transform = 'scale(1.02)';
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled && sessionId) {
            e.currentTarget.style.background = '#2d2dff';
            e.currentTarget.style.transform = 'scale(1)';
          }
        }}
      >
        Send
      </button>
      <button 
        style={disabled ? disabledButtonStyle : recordButtonStyle}
        disabled={!sessionId || disabled}
        onMouseEnter={(e) => {
          if (!disabled && sessionId) {
            e.currentTarget.style.background = '#45a049';
            e.currentTarget.style.transform = 'scale(1.02)';
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled && sessionId) {
            e.currentTarget.style.background = '#4caf50';
            e.currentTarget.style.transform = 'scale(1)';
          }
        }}
      >
        Record
      </button>
    </div>
  );
};

export default MessageInput; 