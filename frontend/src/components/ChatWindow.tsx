import React from 'react';

const ChatWindow: React.FC = () => {
  return (
    <div>
      {/* Example chat bubbles */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ background: '#e0e0e0', borderRadius: 8, padding: 12, maxWidth: 400, marginBottom: 4 }}>Hello! How can I assist you with your football-related questions today?</div>
        <div style={{ fontSize: 12, color: '#888' }}>3:45:37 PM</div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'row-reverse', marginBottom: 16 }}>
        <div>
          <div style={{ background: '#2d2dff', color: '#fff', borderRadius: 8, padding: 12, maxWidth: 400, marginBottom: 4 }}>hi</div>
          <div style={{ fontSize: 12, color: '#888', textAlign: 'right' }}>6:45:27 PM</div>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow; 