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
