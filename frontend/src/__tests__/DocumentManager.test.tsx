import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DocumentManager } from '../components/DocumentManager'

describe('DocumentManager 组件', () => {
  test('应该渲染文档管理界面', () => {
    // Given: 组件被渲染
    render(<DocumentManager />)
    
    // When: 组件加载完成
    // Then: 应该显示文档管理标题
    expect(screen.getByText('文档管理')).toBeInTheDocument()
  })

  test('应该渲染文件上传区域', () => {
    // Given: 组件被渲染
    render(<DocumentManager />)
    
    // When: 组件加载完成
    // Then: 应该显示拖拽上传区域
    expect(screen.getByTestId('drop-zone')).toBeInTheDocument()
  })

  test('应该能够拖拽文件上传', async () => {
    // Given: 组件被渲染
    render(<DocumentManager />)
    const user = userEvent.setup()
    
    // When: 用户拖拽文件到上传区域
    const dropZone = screen.getByTestId('drop-zone')
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' })
    
    // 模拟拖拽事件
    fireEvent.dragOver(dropZone)
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [file]
      }
    })
    
    // Then: 文件应该被添加到文档列表
    await waitFor(() => {
      expect(screen.getByText('test.txt')).toBeInTheDocument()
    })
  })

  test('应该显示文档列表', () => {
    // Given: 组件被渲染
    render(<DocumentManager />)
    
    // When: 组件加载完成
    // Then: 应该显示文档列表容器
    expect(screen.getByTestId('document-list')).toBeInTheDocument()
  })

  test('应该能够删除文档', async () => {
    // Given: 组件被渲染并有一个文档
    render(<DocumentManager />)
    const user = userEvent.setup()
    
    // 模拟添加一个文档
    const dropZone = screen.getByTestId('drop-zone')
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' })
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [file]
      }
    })
    
    // When: 用户点击删除按钮
    await waitFor(() => {
      const deleteButton = screen.getByRole('button', { name: /删除/ })
      user.click(deleteButton)
    })
    
    // Then: 文档应该从列表中移除
    await waitFor(() => {
      expect(screen.queryByText('test.txt')).not.toBeInTheDocument()
    })
  })
})
