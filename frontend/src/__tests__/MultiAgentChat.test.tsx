import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';

// Mock useWebSocket before importing component
vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    isConnected: true,
    lastMessage: null,
    sendMessage: vi.fn(),
  })),
  WebSocketProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import { MultiAgentChat } from '../components/MultiAgentChat';

describe('MultiAgentChat', () => {
  test('renders agent selector', () => {
    render(<MultiAgentChat />);
    expect(screen.getByText(/选择 Agent/)).toBeInTheDocument();
  });

  test('shows available agents', () => {
    render(<MultiAgentChat />);
    expect(screen.getByText('Coder')).toBeInTheDocument();
    expect(screen.getByText('Researcher')).toBeInTheDocument();
    expect(screen.getByText('Tester')).toBeInTheDocument();
  });
});
