import React, { useState, useEffect } from 'react';
import { agentApi, Agent } from '../services/api';

interface AgentListProps {
  onSelectAgent?: (agent: Agent) => void;
  onAgentListUpdate?: (newAgents: Agent[]) => void;
}

const AgentList: React.FC<AgentListProps> = ({ onSelectAgent, onAgentListUpdate }) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newAgent, setNewAgent] = useState({ name: '', prompt: '' });

  // Fetch agents on component mount
  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await agentApi.getAgents();
      setAgents(data);
      if (onAgentListUpdate) onAgentListUpdate(data);
    } catch (err) {
      setError('Failed to fetch agents. Please check your authentication.');
      console.error('Error fetching agents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAgent.name.trim() || !newAgent.prompt.trim()) {
      setError('Name and prompt are required');
      return;
    }

    try {
      setError(null);
      await agentApi.createAgent(newAgent);
      setNewAgent({ name: '', prompt: '' });
      setShowCreateForm(false);
      fetchAgents(); // Refresh the list
    } catch (err) {
      setError('Failed to create agent');
      console.error('Error creating agent:', err);
    }
  };

  const handleUpdateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingAgent) return;

    try {
      setError(null);
      await agentApi.updateAgent(editingAgent.id, {
        name: editingAgent.name,
        prompt: editingAgent.prompt,
      });
      setEditingAgent(null);
      fetchAgents(); // Refresh the list
    } catch (err) {
      setError('Failed to update agent');
      console.error('Error updating agent:', err);
    }
  };

  const handleDeleteAgent = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this agent?')) {
      return;
    }

    try {
      setError(null);
      await agentApi.deleteAgent(id);
      fetchAgents(); // Refresh the list
    } catch (err) {
      setError('Failed to delete agent');
      console.error('Error deleting agent:', err);
    }
  };

  const startEditing = (agent: Agent) => {
    setEditingAgent({ ...agent });
  };

  const cancelEditing = () => {
    setEditingAgent(null);
  };

  if (loading) {
    return (
      <div className="agent-list">
        <h3>Agents</h3>
        <p>Loading agents...</p>
      </div>
    );
  }

  return (
    <div className="agent-list">
      <div className="agent-header">
        <h3>Agents</h3>
        <button 
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn btn-primary"
        >
          {showCreateForm ? 'Cancel' : 'Add Agent'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Create Agent Form */}
      {showCreateForm && (
        <form onSubmit={handleCreateAgent} className="agent-form">
          <h4>Create New Agent</h4>
          <div>
            <label>Name:</label>
            <input
              type="text"
              value={newAgent.name}
              onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
              placeholder="Agent name"
              required
            />
          </div>
          <div>
            <label>Prompt:</label>
            <textarea
              value={newAgent.prompt}
              onChange={(e) => setNewAgent({ ...newAgent, prompt: e.target.value })}
              placeholder="Agent prompt"
              required
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-success">Create</button>
            <button 
              type="button" 
              onClick={() => setShowCreateForm(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Agents List */}
      {agents.length === 0 ? (
        <p>No agents found. Create your first agent!</p>
      ) : (
        <ul className="agents-list">
          {agents.map((agent) => (
            <li key={agent.id} className="agent-item" onClick={() => onSelectAgent && onSelectAgent(agent)} style={{ cursor: 'pointer' }}>
              {editingAgent?.id === agent.id ? (
                // Edit Form
                <form onSubmit={handleUpdateAgent} className="agent-form">
                  <div>
                    <label>Name:</label>
                    <input
                      type="text"
                      value={editingAgent.name}
                      onChange={(e) => setEditingAgent({ ...editingAgent, name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label>Prompt:</label>
                    <textarea
                      value={editingAgent.prompt}
                      onChange={(e) => setEditingAgent({ ...editingAgent, prompt: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-actions">
                    <button type="submit" className="btn btn-success">Save</button>
                    <button type="button" onClick={cancelEditing} className="btn btn-secondary">
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                // Display Mode
                <div className="agent-content">
                  <div className="agent-info">
                    <h4>{agent.name}</h4>
                    <p className="agent-prompt">{agent.prompt}</p>
                    <small>Created: {new Date(agent.created_at).toLocaleDateString()}</small>
                  </div>
                  <div className="agent-actions">
                    <button 
                      onClick={() => startEditing(agent)}
                      className="btn btn-primary"
                    >
                      Edit
                    </button>
                    <button 
                      onClick={() => handleDeleteAgent(agent.id)}
                      className="btn btn-danger"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AgentList; 