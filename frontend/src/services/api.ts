/**
 * API 服务模块
 *
 * 提供与后端 API 的通信功能。
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// ============ 认证相关 ============

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface UserResponse {
  user_id: string;
  username: string;
  email: string;
}

/**
 * 用户登录
 */
export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '登录失败');
  }

  return response.json();
}

/**
 * 用户注册
 */
export async function register(data: RegisterRequest): Promise<UserResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '注册失败');
  }

  return response.json();
}

// ============ 聊天相关 ============

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  agent_thoughts: string;
  conversation_id: string;
}

/**
 * 发送聊天消息
 */
export async function chat(data: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '发送失败');
  }

  return response.json();
}

// ============ 文档管理 ============

export interface DocumentResponse {
  document_id: string;
  filename: string;
  content_type: string;
  uploaded_at: string;
}

/**
 * 上传文档
 */
export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '上传失败');
  }

  return response.json();
}

/**
 * 获取文档列表
 */
export async function listDocuments(): Promise<DocumentResponse[]> {
  const response = await fetch(`${API_BASE_URL}/documents`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '获取失败');
  }

  return response.json();
}

/**
 * 删除文档
 */
export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '删除失败');
  }
}

// ============ RAG 知识库 ============

export interface RAGQueryRequest {
  query: string;
  top_k?: number;
}

export interface RAGQueryResponse {
  status: string;
  documents: string[][];
  distances: number[][];
  ids: string[][];
}

/**
 * 上传文档到知识库
 */
export async function uploadRAGDocument(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/rag/documents`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '上传失败');
  }

  return response.json();
}

/**
 * 获取知识库文档列表
 */
export async function listRAGDocuments(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/rag/documents`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '获取失败');
  }

  return response.json();
}

/**
 * 查询知识库
 */
export async function queryRAG(data: RAGQueryRequest): Promise<RAGQueryResponse> {
  const response = await fetch(`${API_BASE_URL}/rag/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '查询失败');
  }

  return response.json();
}

/**
 * 删除知识库文档
 */
export async function deleteRAGDocument(documentId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/rag/documents/${documentId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '删除失败');
  }

  return response.json();
}

// ============ 对话管理 ============

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface CreateConversationRequest {
  title?: string;
  description?: string;
  user_id: string;
}

export interface UpdateConversationRequest {
  title?: string;
  description?: string;
}

/**
 * 创建对话
 */
export async function createConversation(data: CreateConversationRequest): Promise<Conversation> {
  const response = await fetch(`${API_BASE_URL}/conversations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '创建失败');
  }

  return response.json();
}

/**
 * 获取对话列表
 */
export async function listConversations(userId: string): Promise<Conversation[]> {
  const response = await fetch(`${API_BASE_URL}/conversations?user_id=${userId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '获取失败');
  }

  return response.json();
}

/**
 * 获取单个对话
 */
export async function getConversation(conversationId: string): Promise<Conversation> {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '获取失败');
  }

  return response.json();
}

/**
 * 重命名对话
 */
export async function updateConversation(
  conversationId: string,
  data: UpdateConversationRequest
): Promise<Conversation> {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '更新失败');
  }

  return response.json();
}

/**
 * 删除对话
 */
export async function deleteConversation(conversationId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '删除失败');
  }
}

// ============ Agent 管理 ============

export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  config: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateAgentRequest {
  name: string;
  role: string;
  description?: string;
  config?: string;
  is_active?: number;
}

export interface UpdateAgentRequest {
  name?: string;
  role?: string;
  description?: string;
  config?: string;
  is_active?: number;
}

/**
 * 创建 Agent（仅管理员）
 */
export async function createAgent(data: CreateAgentRequest): Promise<Agent> {
  const response = await fetch(`${API_BASE_URL}/agents`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '创建失败');
  }

  return response.json();
}

/**
 * 获取 Agent 列表
 */
export async function listAgents(activeOnly: boolean = false): Promise<Agent[]> {
  const url = activeOnly 
    ? `${API_BASE_URL}/agents?active_only=true`
    : `${API_BASE_URL}/agents`;
  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '获取失败');
  }

  return response.json();
}

/**
 * 获取单个 Agent
 */
export async function getAgent(agentId: string): Promise<Agent> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '获取失败');
  }

  return response.json();
}

/**
 * 更新 Agent（仅管理员）
 */
export async function updateAgent(
  agentId: string,
  data: UpdateAgentRequest
): Promise<Agent> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '更新失败');
  }

  return response.json();
}

/**
 * 删除 Agent（仅管理员）
 */
export async function deleteAgent(agentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '删除失败');
  }
}

/**
 * 启用 Agent
 */
export async function enableAgent(agentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}/enable`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '启用失败');
  }
}

/**
 * 禁用 Agent
 */
export async function disableAgent(agentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}/disable`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '禁用失败');
  }
}
