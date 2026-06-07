import React, { useState, useEffect } from 'react';
import {
  Agent,
  createAgent,
  listAgents,
  updateAgent,
  deleteAgent,
  enableAgent,
  disableAgent,
} from '../services/api';

export const AgentManager: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    description: '',
    config: '{}',
    is_active: 1,
  });

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setIsLoading(true);
      const data = await listAgents();
      setAgents(data);
    } catch (error) {
      console.error('加载 Agent 列表失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateAgent = async () => {
    try {
      const newAgent = await createAgent({
        name: formData.name,
        role: formData.role,
        description: formData.description,
        config: formData.config,
        is_active: formData.is_active,
      });
      setAgents([newAgent, ...agents]);
      setShowCreateForm(false);
      resetForm();
    } catch (error) {
      console.error('创建 Agent 失败:', error);
      alert('创建 Agent 失败，请检查名称是否已存在');
    }
  };

  const handleUpdateAgent = async (agentId: string) => {
    try {
      const updatedAgent = await updateAgent(agentId, {
        name: formData.name,
        role: formData.role,
        description: formData.description,
        config: formData.config,
        is_active: formData.is_active,
      });
      setAgents(agents.map((a) => (a.id === agentId ? updatedAgent : a)));
      setEditingId(null);
      resetForm();
    } catch (error) {
      console.error('更新 Agent 失败:', error);
      alert('更新 Agent 失败，请检查名称是否已存在');
    }
  };

  const handleDeleteAgent = async (agentId: string) => {
    if (!confirm('确定要删除这个 Agent 吗？')) return;

    try {
      await deleteAgent(agentId);
      setAgents(agents.filter((a) => a.id !== agentId));
    } catch (error) {
      console.error('删除 Agent 失败:', error);
    }
  };

  const handleToggleStatus = async (agentId: string, currentStatus: boolean) => {
    try {
      if (currentStatus) {
        await disableAgent(agentId);
      } else {
        await enableAgent(agentId);
      }
      setAgents(
        agents.map((a) =>
          a.id === agentId ? { ...a, is_active: currentStatus ? 0 : 1 } : a
        )
      );
    } catch (error) {
      console.error('切换 Agent 状态失败:', error);
    }
  };

  const startCreate = () => {
    resetForm();
    setShowCreateForm(true);
    setEditingId(null);
  };

  const startEdit = (agent: Agent) => {
    setFormData({
      name: agent.name,
      role: agent.role,
      description: agent.description,
      config: agent.config,
      is_active: agent.is_active ? 1 : 0,
    });
    setEditingId(agent.id);
    setShowCreateForm(false);
  };

  const cancelForm = () => {
    setShowCreateForm(false);
    setEditingId(null);
    resetForm();
  };

  const resetForm = () => {
    setFormData({
      name: '',
      role: '',
      description: '',
      config: '{}',
      is_active: 1,
    });
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Agent 管理</h2>
        <button
          onClick={startCreate}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          新建 Agent
        </button>
      </div>

      {(showCreateForm || editingId) && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">
            {editingId ? '编辑 Agent' : '新建 Agent'}
          </h3>
          <div className="space-y-4">
            <div>
              <label htmlFor="agent-name" className="block text-sm font-medium text-gray-700 mb-1">
                名称 *
              </label>
              <input
                id="agent-name"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="agent-role" className="block text-sm font-medium text-gray-700 mb-1">
                角色 *
              </label>
              <input
                id="agent-role"
                type="text"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="agent-description" className="block text-sm font-medium text-gray-700 mb-1">
                描述
              </label>
              <textarea
                id="agent-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
            </div>
            <div className="flex space-x-2">
              <button
                onClick={editingId ? () => handleUpdateAgent(editingId) : handleCreateAgent}
                disabled={!formData.name || !formData.role}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {editingId ? '保存' : '创建'}
              </button>
              <button
                onClick={cancelForm}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="text-center text-gray-500 py-8">加载中...</div>
      ) : agents.length === 0 ? (
        <div className="text-center text-gray-500 py-8">暂无 Agent</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-200 rounded-lg overflow-hidden">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">名称</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">角色</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">描述</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {agents.map((agent) => (
                <tr key={agent.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{agent.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{agent.role}</td>
                  <td className="px-6 py-4 text-sm text-gray-500 truncate max-w-xs">{agent.description || '-'}</td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleToggleStatus(agent.id, !!agent.is_active)}
                      className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                        agent.is_active
                          ? 'bg-green-100 text-green-800 hover:bg-green-200'
                          : 'bg-red-100 text-red-800 hover:bg-red-200'
                      }`}
                    >
                      {agent.is_active ? '启用' : '禁用'}
                    </button>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => startEdit(agent)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        编辑
                      </button>
                      <button
                        onClick={() => handleDeleteAgent(agent.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
