import React, { useState, useEffect } from 'react'
import { ChatInterface } from './components/ChatInterface'
import { DocumentManager } from './components/DocumentManager'
import { AuthInterface } from './components/AuthInterface'
import { AgentManager } from './components/AgentManager'
import { WebSocketProvider } from './hooks/useWebSocket'

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'documents' | 'agents'>('chat')

  useEffect(() => {
    const token = localStorage.getItem('authToken')
    if (token) {
      setIsAuthenticated(true)
    }
  }, [])

  const handleAuthSuccess = (token: string) => {
    setIsAuthenticated(true)
    console.log('认证成功，token:', token)
  }

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    setIsAuthenticated(false)
  }

  if (!isAuthenticated) {
    return <AuthInterface onAuthSuccess={handleAuthSuccess} />
  }

  return (
    <WebSocketProvider url="ws://localhost:8000/ws">
      <div className="min-h-screen bg-gray-100">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">AgentForge</h1>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">欢迎使用 AgentForge</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors"
                >
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <nav className="flex space-x-8">
              <button
                onClick={() => setActiveTab('chat')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'chat'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                对话界面
              </button>
              <button
                onClick={() => setActiveTab('documents')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'documents'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                文档管理
              </button>
              <button
                onClick={() => setActiveTab('agents')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'agents'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Agent 管理
              </button>
            </nav>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 min-h-[600px]">
            {activeTab === 'chat' ? (
              <div className="h-[600px] p-6">
                <ChatInterface />
              </div>
            ) : activeTab === 'agents' ? (
              <AgentManager />
            ) : (
              <div className="p-6">
                <DocumentManager />
              </div>
            )}
          </div>
        </main>
      </div>
    </WebSocketProvider>
  )
}

export default App
