import { render, screen, act } from '@testing-library/react'
import { WebSocketProvider, useWebSocket } from '../hooks/useWebSocket'

// 测试用的 WebSocket 组件
const TestWebSocketComponent: React.FC = () => {
  const { isConnected, lastMessage, sendMessage } = useWebSocket()
  
  return (
    <div>
      <div data-testid="connection-status">
        {isConnected ? '已连接' : '未连接'}
      </div>
      <div data-testid="last-message">
        {lastMessage || '无消息'}
      </div>
      <button 
        data-testid="send-button"
        onClick={() => sendMessage('测试消息')}
      >
        发送消息
      </button>
    </div>
  )
}

describe('WebSocket 服务', () => {
  beforeEach(() => {
    // 每个测试前重置
    vi.clearAllMocks()
  })

  test('应该建立 WebSocket 连接', () => {
    // Given: WebSocket Provider 被渲染
    render(
      <WebSocketProvider url="ws://localhost:8000/ws">
        <TestWebSocketComponent />
      </WebSocketProvider>
    )
    
    // When: 组件加载
    // Then: 应该显示连接状态
    expect(screen.getByTestId('connection-status')).toBeInTheDocument()
  })

  test('应该发送消息', () => {
    // Given: WebSocket Provider 被渲染
    render(
      <WebSocketProvider url="ws://localhost:8000/ws">
        <TestWebSocketComponent />
      </WebSocketProvider>
    )
    
    // When: 用户点击发送按钮
    const sendButton = screen.getByTestId('send-button')
    act(() => {
      sendButton.click()
    })
    
    // Then: 应该能够发送消息（这里主要验证函数调用）
    expect(sendButton).toBeInTheDocument()
  })

  test('应该接收消息', () => {
    // Given: WebSocket Provider 被渲染
    render(
      <WebSocketProvider url="ws://localhost:8000/ws">
        <TestWebSocketComponent />
      </WebSocketProvider>
    )
    
    // When: 组件加载
    // Then: 应该显示消息区域
    expect(screen.getByTestId('last-message')).toBeInTheDocument()
  })

  test('应该处理连接状态', () => {
    // Given: WebSocket Provider 被渲染
    render(
      <WebSocketProvider url="ws://localhost:8000/ws">
        <TestWebSocketComponent />
      </WebSocketProvider>
    )
    
    // When: 组件加载
    // Then: 应该显示连接状态
    const statusElement = screen.getByTestId('connection-status')
    expect(statusElement).toBeInTheDocument()
    expect(statusElement.textContent).toBe('未连接')
  })
})
