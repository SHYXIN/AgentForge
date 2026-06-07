import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, test, expect, vi } from 'vitest';
import { ChatInterface } from '../components/ChatInterface';
import { WebSocketProvider } from '../hooks/useWebSocket';

// Mock WebSocket
vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    isConnected: true,
    lastMessage: null,
    sendMessage: vi.fn(),
  })),
  WebSocketProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe('ChatInterface 组件', () => {
  test('应该渲染消息列表', () => {
    render(
      <WebSocketProvider url="ws://localhost:8000/ws">
        <ChatInterface />
      </WebSocketProvider>
    );

    expect(screen.getByTestId('message-list')).toBeInTheDocument();
  });

  test('应该渲染输入框和发送按钮', () => {
    render(
      <WebSocketProvider url="ws://localhost:8000/ws">
        <ChatInterface />
      </WebSocketProvider>
    );

    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /发送/ })).toBeInTheDocument();
  });
});
