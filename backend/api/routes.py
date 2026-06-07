import uuid
"""
API 路由定义模块

使用依赖注入模式，所有 Service 通过 Container 获取。
"""
import os
import tempfile
from datetime import datetime
from typing import List

from fastapi import HTTPException, UploadFile, File, Depends

from backend.models import (
    UserCreate, UserResponse, LoginRequest, LoginResponse,
    DocumentResponse, ChatRequest, ChatResponse,
    RAGDocumentUpload, RAGQueryRequest, RAGQueryResponse, RAGDocumentDelete
)
from backend.container import container
from backend.repositories.base import UserRepository, DocumentRepository


# ============ 用户认证 ============

async def register_user(user: UserCreate):
    """用户注册。"""
    user_repo = container.user_repository()
    
    # 检查用户名是否已存在
    existing = await user_repo.get_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    new_user = await user_repo.create(user)
    
    return UserResponse(
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )


async def login_user(request: LoginRequest):
    """用户登录。"""
    user_repo = container.user_repository()
    
    # 查找用户
    user = await user_repo.get_by_username(request.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if user.password != request.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 生成简单 Token（后续使用 JWT）
    token = f"token-{user.id}"
    return LoginResponse(
        access_token=token,
        token_type="bearer"
    )


# ============ 文档管理 ============

async def upload_document(file: UploadFile = File(...)):
    """上传文档。"""
    content = await file.read()
    
    doc_repo = container.document_repository()
    doc = await doc_repo.create(
        filename=file.filename,
        content_type=file.content_type,
        content=content
    )
    
    return DocumentResponse(
        document_id=doc.id,
        filename=doc.filename,
        content_type=doc.content_type,
        uploaded_at=doc.uploaded_at
    )


async def list_documents():
    """获取文档列表。"""
    doc_repo = container.document_repository()
    documents = await doc_repo.list_all()
    
    return [
        DocumentResponse(
            document_id=doc.id,
            filename=doc.filename,
            content_type=doc.content_type,
            uploaded_at=doc.uploaded_at
        )
        for doc in documents
    ]


# ============ Agent 聊天 ============

async def chat(request: ChatRequest):
    """Agent 聊天端点。"""
        
    # 验证消息不为空
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    # 验证消息长度（限制 10000 字符）
    if len(request.message) > 10000:
        raise HTTPException(status_code=400, detail="消息长度不能超过 10000 字符")

    # 通过 LangChain Agent 处理消息
    from backend.services.langchain_agent import LangChainAgent
    agent = LangChainAgent()
    result = await agent.process_message(request.message, request.conversation_id)

    return ChatResponse(**result)


# ============ RAG 知识库管理 ============

# RAG Pipeline 实例（后续改造为依赖注入）
from backend.services.rag import RAGPipeline
rag_pipeline = RAGPipeline()


async def upload_rag_document(file: UploadFile = File(...)):
    """上传文档到 RAG 知识库。"""
    # 读取文件内容
    content = await file.read()

    # 检查文件类型
    if file.content_type not in ["text/plain", "text/markdown"]:
        raise HTTPException(
            status_code=400,
            detail="仅支持 .txt 和 .md 文件格式"
        )

    # 解码内容
    try:
        text_content = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text_content = content.decode('gbk')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="文件编码不支持，请使用 UTF-8 或 GBK 编码"
            )

    # 生成文档 ID
    document_id = str(uuid.uuid4())

    # 处理文档
    result = rag_pipeline.process_document(
        document=text_content,
        document_id=document_id,
        metadata={
            "filename": file.filename,
            "content_type": file.content_type,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    )

    if result['status'] != 'success':
        raise HTTPException(
            status_code=500,
            detail=f"文档处理失败: {result.get('message', '未知错误')}"
        )

    return RAGDocumentUpload(
        document_id=document_id,
        filename=file.filename,
        content_type=file.content_type,
        chunks_count=result['chunks_count'],
        status="success"
    )


async def list_rag_documents():
    """获取 RAG 知识库文档列表。"""
    # 这里需要从 RAG Pipeline 获取文档列表
    # 暂时返回空列表，后续实现
    return []


async def query_rag(request: RAGQueryRequest):
    """查询 RAG 知识库。"""
    # 验证查询不为空
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="查询内容不能为空")

    # 验证 top_k
    if request.top_k < 1 or request.top_k > 20:
        raise HTTPException(status_code=400, detail="top_k 必须在 1-20 之间")

    # 执行查询
    result = rag_pipeline.query(
        query_text=request.query,
        top_k=request.top_k
    )

    if result['status'] != 'success':
        raise HTTPException(
            status_code=500,
            detail=f"查询失败: {result.get('message', '未知错误')}"
        )

    return RAGQueryResponse(
        status="success",
        documents=result.get('documents', [[]]),
        distances=result.get('distances', [[]]),
        ids=result.get('ids', [[]])
    )


async def delete_rag_document(document_id: str):
    """删除 RAG 知识库文档。"""
    # 从向量存储中删除
    result = rag_pipeline.delete_document(document_id)

    return RAGDocumentDelete(
        status="success",
        document_id=document_id,
        message="文档删除成功"
    )
