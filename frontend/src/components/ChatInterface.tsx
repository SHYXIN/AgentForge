import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { ConversationSidebar } from './ConversationSidebar';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  agentThoughts?: string;
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [agentThoughts, setAgentThoughts] = useState('等待输入...');
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [userId] = useState('user-123'); // TODO: 从认证上下文获取
  const [conversationVersion, setConversationVersion] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageCounter = useRef(0);

  const { isConnected, lastMessage, sendMessage } = useWebSocket('ws://localhost:8000/ws');

  useEffect(() => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);

        if (data.type === 'chat_response') {
          messageCounter.current += 1;
          const agentMessage: Message = {
            id: `agent-${Date.now()}-${messageCounter.current}`,
            content: data.response,
            sender: 'agent',
            timestamp: new Date(),
            agentThoughts: data.agent_thoughts,
          };

          setMessages(prev => [...prev, agentMessage]);
          setIsStreaming(false);
          setAgentThoughts(data.agent_thoughts || '完成');
        }
      } catch (e) {
        console.error('解析消息失败:', e);
      }
    }
  }, [lastMessage]);

  const handleSendMessage = () => {
    if (!inputValue.trim() || !isConnected) return;

    messageCounter.current += 1;
    const newMessage: Message = {
      id: `user-${Date.now()}-${messageCounter.current}`,
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');
    setIsStreaming(true);
    setAgentThoughts('正在思考...');

    sendMessage(JSON.stringify({
      type: 'chat',
      message: inputValue,
      conversation_id: currentConversationId
    }));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleConversationSelect = (conversationId: string) => {
    setCurrentConversationId(conversationId);
    setMessages([]);
    setAgentThoughts('等待输入...');
  };

  const handleConversationChange = () => {
    setConversationVersion(prev => prev + 1);
  };

  return (
    <div className="flex h-full bg-white rounded-lg shadow-md">
      {/* 对话管理侧边栏 */}
      <ConversationSidebar
        userId={userId}
        currentConversationId={currentConversationId}
        onConversationSelect={handleConversationSelect}
        onConversationChange={handleConversationChange}
      />

      {/* 聊天主区域 */}
      <div className="flex-1 flex flex-col">
        {/* 连接状态 */}
        <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
          <span className={`text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
            {isConnected ? '已连接' : '未连接'}
          </span>
          {currentConversationId && (
            <span className="ml-4 text-sm text-gray-600">
              当前对话: {currentConversationId}
            </span>
          )}
        </div>

        {/* 消息列表 */}
        <div
          data-testid="message-list"
          className="flex-1 p-4 overflow-y-auto space-y-4"
        >
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              {currentConversationId ? '开始与 AgentForge 对话吧！' : '请选择一个对话或创建新对话'}
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.sender === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))
          )}

          {isStreaming && (
            <div
              data-testid="streaming-indicator"
              className="flex justify-start"
            >
              <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Agent 思考过程 */}
        <div
          data-testid="thinking-process"
          className="px-4 py-2 bg-gray-50 border-t border-gray-200"
        >
          <div className="text-sm text-gray-600">
            思考过程: {agentThoughts}
          </div>
        </div>

        {/* 输入区域 */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={currentConversationId ? "输入消息..." : "请先选择或创建一个对话"}
              disabled={!currentConversationId}
              className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              rows={1}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || !isConnected || !currentConversationId}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
