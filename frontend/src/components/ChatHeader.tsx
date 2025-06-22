import React from 'react';

const ChatHeader: React.FC = () => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div>
        <span style={{ fontWeight: 'bold', fontSize: 20 }}>football agent</span>
        <span style={{ marginLeft: 16, fontStyle: 'italic', fontSize: 14, color: '#e0e0e0' }}>agent's name</span>
      </div>
      <div>
        <span>Chat 1 (08:43:41 PM)</span>
      </div>
    </div>
  );
};

export default ChatHeader; 