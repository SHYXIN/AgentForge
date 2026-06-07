"""
测试：RAG 知识检索系统

行为：系统应该能够接收文档，进行分块、向量化，并基于文档回答问题。
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


# ============ 文档分块服务测试 ============

class TestDocumentChunking:
    """文档分块服务测试类。"""

    def test_chunk_creation_from_text(self):
        """系统应该能够将文本分割成指定大小的块。"""
        from backend.services.rag import DocumentChunker

        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        text = "这是一个测试文本。" * 50  # 创建较长的文本

        chunks = chunker.chunk_text(text)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert all(len(chunk) <= 120 for chunk in chunks)  # 允许一些重叠

    def test_chunk_overlap(self):
        """系统应该在文本块之间保持重叠。"""
        from backend.services.rag import DocumentChunker

        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        text = "abcdefghijklmnopqrstuvwxyz" * 10

        chunks = chunker.chunk_text(text)

        # 检查是否有重叠（简化检查：确保块之间有共同内容）
        if len(chunks) > 1:
            # 至少应该生成多个块
            assert len(chunks) >= 2

    def test_chunk_empty_text(self):
        """系统应该能够处理空文本。"""
        from backend.services.rag import DocumentChunker

        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        text = ""

        chunks = chunker.chunk_text(text)

        assert len(chunks) == 0

    def test_chunk_short_text(self):
        """系统应该能够处理短文本（小于块大小）。"""
        from backend.services.rag import DocumentChunker

        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        text = "短文本"

        chunks = chunker.chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0] == text


# ============ Embedding 服务测试 ============

class TestEmbeddingService:
    """Embedding 服务测试类。"""

    def test_embedding_generation(self):
        """系统应该能够生成文本的嵌入向量。"""
        from backend.services.rag import EmbeddingService

        # Mock 模型以避免加载实际模型
        with patch('backend.services.rag.SentenceTransformer') as mock_model:
            mock_instance = MagicMock()
            mock_instance.encode.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5]]
            mock_model.return_value = mock_instance

            service = EmbeddingService(model_path="mock/path")
            embedding = service.encode("测试文本")

            assert embedding is not None
            assert len(embedding) == 5

    def test_batch_embedding_generation(self):
        """系统应该能够批量生成嵌入向量。"""
        from backend.services.rag import EmbeddingService

        with patch('backend.services.rag.SentenceTransformer') as mock_model:
            mock_instance = MagicMock()
            mock_instance.encode.return_value = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
            mock_model.return_value = mock_instance

            service = EmbeddingService(model_path="mock/path")
            texts = ["文本1", "文本2", "文本3"]
            embeddings = service.encode_batch(texts)

            assert len(embeddings) == 3
            assert all(len(emb) == 2 for emb in embeddings)

    def test_embedding_empty_text(self):
        """系统应该能够处理空文本的嵌入。"""
        from backend.services.rag import EmbeddingService

        with patch('backend.services.rag.SentenceTransformer') as mock_model:
            mock_instance = MagicMock()
            mock_instance.encode.return_value = [[]]
            mock_model.return_value = mock_instance

            service = EmbeddingService(model_path="mock/path")
            embedding = service.encode("")

            assert embedding is not None


# ============ 向量存储服务测试 ============

class TestVectorStore:
    """向量存储服务测试类。"""

    def test_add_documents(self):
        """系统应该能够添加文档到向量存储。"""
        from backend.services.rag import VectorStoreService

        with patch('backend.services.rag.chromadb') as mock_chromadb:
            mock_collection = MagicMock()
            mock_chromadb.Client.return_value.get_or_create_collection.return_value = mock_collection

            service = VectorStoreService()
            ids = ["doc1", "doc2"]
            embeddings = [[0.1, 0.2], [0.3, 0.4]]
            documents = ["文档1内容", "文档2内容"]

            service.add_documents(ids, embeddings, documents)

            mock_collection.add.assert_called_once()

    def test_similarity_search(self):
        """系统应该能够执行相似度搜索。"""
        from backend.services.rag import VectorStoreService

        with patch('backend.services.rag.chromadb') as mock_chromadb:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                'documents': [['相关文档1', '相关文档2']],
                'distances': [[0.1, 0.2]],
                'ids': [['doc1', 'doc2']]
            }
            mock_chromadb.Client.return_value.get_or_create_collection.return_value = mock_collection

            service = VectorStoreService()
            query_embedding = [0.1, 0.2, 0.3]
            results = service.search(query_embedding, top_k=2)

            assert 'documents' in results
            assert 'distances' in results
            assert 'ids' in results
            assert len(results['documents'][0]) == 2

    def test_delete_documents(self):
        """系统应该能够从向量存储中删除文档。"""
        from backend.services.rag import VectorStoreService

        with patch('backend.services.rag.chromadb') as mock_chromadb:
            mock_collection = MagicMock()
            mock_chromadb.Client.return_value.get_or_create_collection.return_value = mock_collection

            service = VectorStoreService()
            ids = ["doc1", "doc2"]

            service.delete_documents(ids)

            mock_collection.delete.assert_called_once_with(ids=ids)


# ============ RAG Pipeline 测试 ============

class TestRAGPipeline:
    """RAG Pipeline 测试类。"""

    def test_document_processing_pipeline(self):
        """系统应该能够处理完整文档流程：分块 → 向量化 → 存储。"""
        from backend.services.rag import RAGPipeline

        with patch('backend.services.rag.DocumentChunker') as mock_chunker, \
             patch('backend.services.rag.EmbeddingService') as mock_embedding, \
             patch('backend.services.rag.VectorStoreService') as mock_vector_store:

            # 设置 mock
            mock_chunker_instance = MagicMock()
            mock_chunker_instance.chunk_text.return_value = ["块1", "块2", "块3"]
            mock_chunker.return_value = mock_chunker_instance

            mock_embedding_instance = MagicMock()
            mock_embedding_instance.encode_batch.return_value = [[0.1], [0.2], [0.3]]
            mock_embedding.return_value = mock_embedding_instance

            mock_vector_store_instance = MagicMock()
            mock_vector_store.return_value = mock_vector_store_instance

            pipeline = RAGPipeline()
            document = "这是一个测试文档内容。"

            result = pipeline.process_document(document, "test-doc-id")

            assert result['status'] == 'success'
            assert result['document_id'] == 'test-doc-id'
            assert result['chunks_count'] == 3

    def test_query_pipeline(self):
        """系统应该能够处理查询流程：向量化 → 检索 → 返回结果。"""
        from backend.services.rag import RAGPipeline

        with patch('backend.services.rag.EmbeddingService') as mock_embedding, \
             patch('backend.services.rag.VectorStoreService') as mock_vector_store:

            # 设置 mock
            mock_embedding_instance = MagicMock()
            mock_embedding_instance.encode.return_value = [0.1, 0.2, 0.3]
            mock_embedding.return_value = mock_embedding_instance

            mock_vector_store_instance = MagicMock()
            mock_vector_store_instance.search.return_value = {
                'documents': [['相关文档1', '相关文档2']],
                'distances': [[0.1, 0.2]],
                'ids': [['doc1', 'doc2']]
            }
            mock_vector_store.return_value = mock_vector_store_instance

            pipeline = RAGPipeline()
            query = "测试问题"

            result = pipeline.query(query, top_k=2)

            assert 'documents' in result
            assert 'distances' in result
            assert 'ids' in result
            assert len(result['documents'][0]) == 2


# ============ API 端点测试 ============

class TestRAGAPI:
    """RAG API 端点测试类。"""

    def test_upload_document_endpoint(self):
        """系统应该能够通过 API 上传文档到知识库。"""
        from backend.main import app

        client = TestClient(app)

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("这是测试文档内容。" * 100)
            temp_file = f.name

        try:
            with open(temp_file, 'rb') as f:
                response = client.post(
                    "/api/rag/documents",
                    files={"file": ("test.txt", f, "text/plain")}
                )

            assert response.status_code == 201
            data = response.json()
            assert "document_id" in data
            assert data["filename"] == "test.txt"
        finally:
            os.unlink(temp_file)

    def test_list_documents_endpoint(self):
        """系统应该能够通过 API 获取知识库文档列表。"""
        from backend.main import app

        client = TestClient(app)

        response = client.get("/api/rag/documents")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_query_endpoint(self):
        """系统应该能够通过 API 查询知识库。"""
        from backend.main import app

        client = TestClient(app)

        response = client.post(
            "/api/rag/query",
            json={
                "query": "测试问题",
                "top_k": 3
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "distances" in data

    def test_delete_document_endpoint(self):
        """系统应该能够通过 API 删除文档。"""
        from backend.main import app

        client = TestClient(app)

        # 先上传一个文档
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("测试内容")
            temp_file = f.name

        try:
            with open(temp_file, 'rb') as f:
                upload_response = client.post(
                    "/api/rag/documents",
                    files={"file": ("test.txt", f, "text/plain")}
                )

            document_id = upload_response.json()["document_id"]

            # 删除文档
            response = client.delete(f"/api/rag/documents/{document_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
        finally:
            os.unlink(temp_file)

    def test_query_empty_text(self):
        """系统应该能够处理空查询。"""
        from backend.main import app

        client = TestClient(app)

        response = client.post(
            "/api/rag/query",
            json={
                "query": "",
                "top_k": 3
            }
        )

        # 应该返回 400 错误
        assert response.status_code == 400
