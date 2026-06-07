import React, { useState, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
}

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  agentName?: string;
  timestamp: Date;
}

const AVAILABLE_AGENTS: Agent[] = [
  { id: 'coder', name: 'Coder', role: '代码工程师', description: '编写和优化代码' },
  { id: 'researcher', name: 'Researcher', role: '研究员', description: '信息检索和分析' },
  { id: 'tester', name: 'Tester', role: '测试工程师', description: '测试和代码审查' },
];

export const MultiAgentChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<Agent>(AVAILABLE_AGENTS[0]);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { isConnected, lastMessage, sendMessage } = useWebSocket('ws://localhost:8000/ws');

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  React.useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);

        if (data.type === 'chat_response') {
          const agentMessage: Message = {
            id: Date.now().toString(),
            content: data.response,
            sender: 'agent',
            agentName: selectedAgent.name,
            timestamp: new Date(),
          };

          setMessages(prev => [...prev, agentMessage]);
          setIsStreaming(false);
        }
      } catch (e) {
        console.error('解析消息失败:', e);
      }
    }
  }, [lastMessage, selectedAgent.name]);

  const handleSendMessage = () => {
    if (!inputValue.trim() || !isConnected) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');
    setIsStreaming(true);

    sendMessage(JSON.stringify({
      type: 'chat',
      message: inputValue,
      agent: selectedAgent.id,
    }));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-md">
      {/* Agent 选择器 */}
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">选择 Agent:</span>
          {AVAILABLE_AGENTS.map(agent => (
            <button
              key={agent.id}
              onClick={() => setSelectedAgent(agent)}
              className={`px-3 py-1 text-sm rounded-full transition-colors ${
                selectedAgent.id === agent.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {agent.name}
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-1">{selectedAgent.description}</p>
      </div>

      {/* 连接状态 */}
      <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
        <span className={`text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
          {isConnected ? `已连接 - 当前 Agent: ${selectedAgent.name}` : '未连接'}
        </span>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            开始与 {selectedAgent.name} 对话吧！
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
                {message.sender === 'agent' && message.agentName && (
                  <div className="text-xs text-gray-500 mb-1">{message.agentName}</div>
                )}
                {message.content}
              </div>
            </div>
          ))
        )}

        {isStreaming && (
          <div className="flex justify-start">
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

      {/* 输入区域 */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入消息..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={1}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || !isConnected}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            发送
          </button>
        </div>
      </div>
    </div>
  );
};
