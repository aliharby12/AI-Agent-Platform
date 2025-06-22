import React from 'react';

const MessageInput: React.FC = () => {
  return (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <input type="text" placeholder="Type your message or use voice..." style={{ flex: 1, padding: 12, borderRadius: 4, border: '1px solid #ccc', marginRight: 8 }} />
      <button style={{ background: '#2d2dff', color: '#fff', border: 'none', borderRadius: 4, padding: '8px 16px', marginRight: 8 }}>Send</button>
      <button style={{ background: '#4caf50', color: '#fff', border: 'none', borderRadius: 4, padding: '8px 16px' }}>Record</button>
    </div>
  );
};

export default MessageInput; 