import { render, screen } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';
import { DocumentManager } from '../components/DocumentManager';

// Mock fetch
global.fetch = vi.fn();

describe('DocumentManager 组件', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('应该渲染文档管理界面', () => {
    render(<DocumentManager />);

    expect(screen.getByText('文档管理')).toBeInTheDocument();
  });

  test('应该显示上传区域', () => {
    render(<DocumentManager />);

    expect(screen.getByText(/点击选择文件/)).toBeInTheDocument();
  });
});
