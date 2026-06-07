import React, { useState, useEffect } from 'react';
import {
  Conversation,
  createConversation,
  listConversations,
  updateConversation,
  deleteConversation,
} from '../services/api';

interface ConversationSidebarProps {
  userId: string;
  currentConversationId: string | null;
  onConversationSelect: (conversationId: string) => void;
  onConversationChange: () => void;
}

export const ConversationSidebar: React.FC<ConversationSidebarProps> = ({
  userId,
  currentConversationId,
  onConversationSelect,
  onConversationChange,
}) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');

  useEffect(() => {
    loadConversations();
  }, [userId]);

  const loadConversations = async () => {
    try {
      setIsLoading(true);
      const data = await listConversations(userId);
      setConversations(data);
    } catch (error) {
      console.error('加载对话列表失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateConversation = async () => {
    try {
      const newConversation = await createConversation({
        title: '新对话',
        description: '',
        user_id: userId,
      });
      setConversations([newConversation, ...conversations]);
      onConversationSelect(newConversation.id);
      onConversationChange();
    } catch (error) {
      console.error('创建对话失败:', error);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    if (!confirm('确定要删除这个对话吗？')) return;

    try {
      await deleteConversation(conversationId);
      setConversations(conversations.filter((c) => c.id !== conversationId));
      onConversationChange();
    } catch (error) {
      console.error('删除对话失败:', error);
    }
  };

  const handleStartRename = (conversation: Conversation) => {
    setEditingId(conversation.id);
    setEditingTitle(conversation.title);
  };

  const handleSaveRename = async (conversationId: string) => {
    if (!editingTitle.trim()) return;

    try {
      await updateConversation(conversationId, { title: editingTitle.trim() });
      setConversations(
        conversations.map((c) =>
          c.id === conversationId ? { ...c, title: editingTitle.trim() } : c
        )
      );
      setEditingId(null);
      setEditingTitle('');
      onConversationChange();
    } catch (error) {
      console.error('重命名对话失败:', error);
    }
  };

  const handleCancelRename = () => {
    setEditingId(null);
    setEditingTitle('');
  };

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">对话列表</h2>
        </div>
        <button
          onClick={handleCreateConversation}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>新建对话</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">加载中...</div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500">暂无对话，点击上方按钮创建</div>
        ) : (
          <div className="space-y-1 p-2">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                  currentConversationId === conversation.id
                    ? 'bg-blue-50 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => onConversationSelect(conversation.id)}
              >
                {editingId === conversation.id ? (
                  <input
                    type="text"
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onBlur={() => handleSaveRename(conversation.id)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') handleSaveRename(conversation.id);
                      else if (e.key === 'Escape') handleCancelRename();
                    }}
                    className="flex-1 px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                    onClick={(e) => e.stopPropagation()}
                  />
                ) : (
                  <>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {conversation.title}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(conversation.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleStartRename(conversation); }}
                        className="p-1 text-gray-500 hover:text-blue-600 rounded"
                        title="重命名"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDeleteConversation(conversation.id); }}
                        className="p-1 text-gray-500 hover:text-red-600 rounded"
                        title="删除"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
