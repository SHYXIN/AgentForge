import { render, screen } from '@testing-library/react';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import { AgentManager } from '../components/AgentManager';
import * as api from '../services/api';

vi.mock('../services/api', () => ({
  createAgent: vi.fn(),
  listAgents: vi.fn(),
  updateAgent: vi.fn(),
  deleteAgent: vi.fn(),
  enableAgent: vi.fn(),
  disableAgent: vi.fn(),
}));

describe('AgentManager 组件', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (api.listAgents as any).mockResolvedValue([]);
  });

  test('应该渲染 Agent 管理标题', () => {
    render(<AgentManager />);
    expect(screen.getByText('Agent 管理')).toBeInTheDocument();
  });

  test('应该渲染新建 Agent 按钮', () => {
    render(<AgentManager />);
    expect(screen.getByText('新建 Agent')).toBeInTheDocument();
  });

  test('空 Agent 列表应该显示提示信息', async () => {
    (api.listAgents as any).mockResolvedValue([]);
    render(<AgentManager />);
    
    await new Promise(resolve => setTimeout(resolve, 100));
    expect(screen.getByText('暂无 Agent')).toBeInTheDocument();
  });
});
