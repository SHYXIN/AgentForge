import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, test, expect, vi } from 'vitest';
import { AuthInterface } from '../components/AuthInterface';

// Mock fetch
global.fetch = vi.fn();

describe('AuthInterface 组件', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('应该渲染登录表单', () => {
    render(<AuthInterface />);

    expect(screen.getByRole('heading', { name: /登录/ })).toBeInTheDocument();
    expect(screen.getByLabelText('用户名')).toBeInTheDocument();
    expect(screen.getByLabelText('密码')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^登录$/ })).toBeInTheDocument();
  });

  test('应该能够切换到注册表单', async () => {
    render(<AuthInterface />);
    const user = userEvent.setup();

    // Click register link
    const registerLink = screen.getByText('没有账户？立即注册');
    await user.click(registerLink);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /注册/ })).toBeInTheDocument();
    });
  });
});
