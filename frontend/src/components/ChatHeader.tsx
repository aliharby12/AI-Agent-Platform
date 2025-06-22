import React, { useEffect, useState } from 'react';
import { Agent, ChatSession, sessionApi } from '../services/api';

interface ChatHeaderProps {
  selectedAgent: Agent | null;
  selectedSession: ChatSession | null;
  onSelectSession: (session: ChatSession | null) => void;
  agents: Agent[];
}

const ChatHeader: React.FC<ChatHeaderProps> = ({ selectedAgent, selectedSession, onSelectSession, agents }) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedAgent) {
      setLoading(true);
      sessionApi.listSessions(selectedAgent.id)
        .then(setSessions)
        .finally(() => setLoading(false));
    } else {
      setSessions([]);
    }
  }, [selectedAgent]);

  const noAgents = agents.length === 0;

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
      <div>
        <span style={{ fontWeight: 'bold', fontSize: 20 }}>{noAgents ? 'No Agents' : (selectedAgent ? selectedAgent.name : 'No agent selected')}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        {noAgents ? (
          <span style={{ color: '#e0e0e0' }}>No Agents</span>
        ) : selectedAgent ? (
          loading ? (
            <span>Loading sessions...</span>
          ) : (
            <select
              value={selectedSession ? selectedSession.id : ''}
              onChange={e => {
                const session = sessions.find(s => s.id === Number(e.target.value));
                onSelectSession(session || null);
              }}
              style={{ padding: 8, borderRadius: 4 }}
            >
              <option value="">Select session</option>
              {sessions.map(session => (
                <option key={session.id} value={session.id}>
                  Session #{session.id} ({new Date(session.created_at).toLocaleString()})
                </option>
              ))}
            </select>
          )
        ) : (
          <span style={{ color: '#e0e0e0' }}>No agent selected</span>
        )}
      </div>
    </div>
  );
};

export default ChatHeader; 