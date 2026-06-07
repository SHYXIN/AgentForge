import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import { ConversationSidebar } from '../components/ConversationSidebar';
import * as api from '../services/api';

vi.mock('../services/api', () => ({
  createConversation: vi.fn(),
  listConversations: vi.fn(),
  updateConversation: vi.fn(),
  deleteConversation: vi.fn(),
}));

describe('ConversationSidebar 组件', () => {
  const mockOnConversationSelect = vi.fn();
  const mockOnConversationChange = vi.fn();

  const defaultProps = {
    userId: 'user-123',
    currentConversationId: null,
    onConversationSelect: mockOnConversationSelect,
    onConversationChange: mockOnConversationChange,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (api.listConversations as any).mockResolvedValue([]);
  });

  test('应该渲染对话列表标题', async () => {
    render(<ConversationSidebar {...defaultProps} />);
    expect(screen.getByText('对话列表')).toBeInTheDocument();
  });

  test('应该渲染新建对话按钮', () => {
    render(<ConversationSidebar {...defaultProps} />);
    expect(screen.getByText('新建对话')).toBeInTheDocument();
  });

  test('点击新建对话按钮应该创建新对话', async () => {
    const newConversation = {
      id: 'new-conv-id',
      title: '新对话',
      description: '',
      user_id: 'user-123',
      is_active: true,
      created_at: '2026-06-07T00:00:00Z',
      updated_at: '2026-06-07T00:00:00Z',
      message_count: 0,
    };
    (api.createConversation as any).mockResolvedValue(newConversation);

    render(<ConversationSidebar {...defaultProps} />);

    const createButton = screen.getByText('新建对话');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(api.createConversation).toHaveBeenCalledWith({
        title: '新对话',
        description: '',
        user_id: 'user-123',
      });
      expect(mockOnConversationSelect).toHaveBeenCalledWith('new-conv-id');
      expect(mockOnConversationChange).toHaveBeenCalled();
    });
  });

  test('应该显示对话列表', async () => {
    const conversations = [
      {
        id: 'conv-1',
        title: '对话 1',
        description: '',
        user_id: 'user-123',
        is_active: true,
        created_at: '2026-06-07T00:00:00Z',
        updated_at: '2026-06-07T00:00:00Z',
        message_count: 5,
      },
      {
        id: 'conv-2',
        title: '对话 2',
        description: '',
        user_id: 'user-123',
        is_active: true,
        created_at: '2026-06-06T00:00:00Z',
        updated_at: '2026-06-06T00:00:00Z',
        message_count: 3,
      },
    ];
    (api.listConversations as any).mockResolvedValue(conversations);

    render(<ConversationSidebar {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('对话 1')).toBeInTheDocument();
      expect(screen.getByText('对话 2')).toBeInTheDocument();
    });
  });

  test('应该能选择对话', async () => {
    const conversations = [
      {
        id: 'conv-1',
        title: '对话 1',
        description: '',
        user_id: 'user-123',
        is_active: true,
        created_at: '2026-06-07T00:00:00Z',
        updated_at: '2026-06-07T00:00:00Z',
        message_count: 5,
      },
    ];
    (api.listConversations as any).mockResolvedValue(conversations);

    render(<ConversationSidebar {...defaultProps} />);

    await waitFor(() => {
      const conversationItem = screen.getByText('对话 1');
      fireEvent.click(conversationItem);
      expect(mockOnConversationSelect).toHaveBeenCalledWith('conv-1');
    });
  });

  test('空对话列表应该显示提示信息', async () => {
    (api.listConversations as any).mockResolvedValue([]);

    render(<ConversationSidebar {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('暂无对话，点击上方按钮创建')).toBeInTheDocument();
    });
  });
});
