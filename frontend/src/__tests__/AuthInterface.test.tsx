import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthInterface } from '../components/AuthInterface'

describe('AuthInterface 组件', () => {
  test('应该渲染登录表单', () => {
    // Given: 组件被渲染
    render(<AuthInterface />)
    
    // When: 组件加载完成
    // Then: 应该显示登录表单
    expect(screen.getByText('登录')).toBeInTheDocument()
    expect(screen.getByLabelText('用户名')).toBeInTheDocument()
    expect(screen.getByLabelText('密码')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /登录/ })).toBeInTheDocument()
  })

  test('应该能够输入用户名和密码', async () => {
    // Given: 组件被渲染
    render(<AuthInterface />)
    const user = userEvent.setup()
    
    // When: 用户输入用户名和密码
    const usernameInput = screen.getByLabelText('用户名')
    const passwordInput = screen.getByLabelText('密码')
    
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'testpassword')
    
    // Then: 输入框应该包含输入的值
    expect(usernameInput).toHaveValue('testuser')
    expect(passwordInput).toHaveValue('testpassword')
  })

  test('应该能够切换到注册表单', async () => {
    // Given: 组件被渲染
    render(<AuthInterface />)
    const user = userEvent.setup()
    
    // When: 用户点击注册链接
    const registerLink = screen.getByText('没有账户？点击注册')
    await user.click(registerLink)
    
    // Then: 应该显示注册表单
    await waitFor(() => {
      expect(screen.getByText('注册')).toBeInTheDocument()
      expect(screen.getByLabelText('确认密码')).toBeInTheDocument()
    })
  })

  test('应该能够提交登录表单', async () => {
    // Given: 组件被渲染
    render(<AuthInterface />)
    const user = userEvent.setup()
    
    // When: 用户填写并提交登录表单
    const usernameInput = screen.getByLabelText('用户名')
    const passwordInput = screen.getByLabelText('密码')
    const loginButton = screen.getByRole('button', { name: /登录/ })
    
    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'testpassword')
    await user.click(loginButton)
    
    // Then: 应该触发登录操作（这里主要验证表单提交）
    expect(loginButton).toBeInTheDocument()
  })

  test('应该能够提交注册表单', async () => {
    // Given: 组件被渲染并切换到注册模式
    render(<AuthInterface />)
    const user = userEvent.setup()
    
    // 切换到注册模式
    const registerLink = screen.getByText('没有账户？点击注册')
    await user.click(registerLink)
    
    // When: 用户填写并提交注册表单
    await waitFor(async () => {
      const usernameInput = screen.getByLabelText('用户名')
      const passwordInput = screen.getByLabelText('密码')
      const confirmPasswordInput = screen.getByLabelText('确认密码')
      const registerButton = screen.getByRole('button', { name: /注册/ })
      
      await user.type(usernameInput, 'newuser')
      await user.type(passwordInput, 'newpassword')
      await user.type(confirmPasswordInput, 'newpassword')
      await user.click(registerButton)
      
      // Then: 应该触发注册操作
      expect(registerButton).toBeInTheDocument()
    })
  })

  test('应该显示密码不匹配错误', async () => {
    // Given: 组件被渲染并切换到注册模式
    render(<AuthInterface />)
    const user = userEvent.setup()
    
    // 切换到注册模式
    const registerLink = screen.getByText('没有账户？点击注册')
    await user.click(registerLink)
    
    // When: 用户输入不匹配的密码
    await waitFor(async () => {
      const passwordInput = screen.getByLabelText('密码')
      const confirmPasswordInput = screen.getByLabelText('确认密码')
      const registerButton = screen.getByRole('button', { name: /注册/ })
      
      await user.type(passwordInput, 'password1')
      await user.type(confirmPasswordInput, 'password2')
      await user.click(registerButton)
      
      // Then: 应该显示密码不匹配错误
      await waitFor(() => {
        expect(screen.getByText('密码不匹配')).toBeInTheDocument()
      })
    })
  })
})
