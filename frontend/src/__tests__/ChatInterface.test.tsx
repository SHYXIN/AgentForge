import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatInterface } from '../components/ChatInterface'

describe('ChatInterface 组件', () => {
  test('应该渲染消息列表', () => {
    // Given: 组件被渲染
    render(<ChatInterface />)
    
    // When: 组件加载完成
    // Then: 应该显示消息列表容器
    expect(screen.getByTestId('message-list')).toBeInTheDocument()
  })

  test('应该渲染输入框和发送按钮', () => {
    // Given: 组件被渲染
    render(<ChatInterface />)
    
    // When: 组件加载完成
    // Then: 应该显示输入框和发送按钮
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /发送/ })).toBeInTheDocument()
  })

  test('应该能够输入消息并发送', async () => {
    // Given: 组件被渲染
    render(<ChatInterface />)
    const user = userEvent.setup()
    
    // When: 用户输入消息并点击发送
    const input = screen.getByRole('textbox')
    const sendButton = screen.getByRole('button', { name: /发送/ })
    
    await user.type(input, '你好，AgentForge!')
    await user.click(sendButton)
    
    // Then: 消息应该被添加到消息列表
    await waitFor(() => {
      expect(screen.getByText('你好，AgentForge!')).toBeInTheDocument()
    })
  })

  test('应该显示流式输出', async () => {
    // Given: 组件被渲染
    render(<ChatInterface />)
    
    // When: 模拟流式输出
    // Then: 应该显示流式输出指示器
    // 这里我们会在实现中添加具体的流式输出逻辑
    expect(screen.getByTestId('streaming-indicator')).toBeInTheDocument()
  })

  test('应该显示 Agent 思考过程', () => {
    // Given: 组件被渲染
    render(<ChatInterface />)
    
    // When: 组件加载完成
    // Then: 应该显示思考过程区域
    expect(screen.getByTestId('thinking-process')).toBeInTheDocument()
  })
})
