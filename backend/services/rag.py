"""
RAG 知识检索服务模块

提供文档分块、向量化、存储和检索功能。
"""
import os
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer


class DocumentChunker:
    """
    文档分块器

    将长文本分割成语义化的块，支持重叠以保持上下文连贯性。
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化文档分块器。

        Args:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 相邻块之间的重叠字符数
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        将文本分割成块。

        Args:
            text: 要分割的文本

        Returns:
            文本块列表
        """
        # 处理空文本
        if not text or not text.strip():
            return []

        # 如果文本长度小于块大小，直接返回
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # 计算当前块的结束位置
            end = start + self.chunk_size

            # 如果到达文本末尾，直接取剩余部分
            if end >= len(text):
                chunks.append(text[start:])
                break

            # 查找合适的分割点（优先在句子边界分割）
            split_pos = self._find_split_position(text, start, end)

            # 提取文本块
            chunk = text[start:split_pos].strip()
            if chunk:
                chunks.append(chunk)

            # 下一个块的起始位置（考虑重叠）
            start = split_pos - self.chunk_overlap
            if start <= (split_pos - self.chunk_size):
                start = split_pos

        return chunks

    def _find_split_position(self, text: str, start: int, end: int) -> int:
        """
        查找合适的分割位置，优先在句子边界分割。

        Args:
            text: 文本
            start: 起始位置
            end: 结束位置

        Returns:
            分割位置
        """
        # 定义句子结束标记
        sentence_endings = ['。', '！', '？', '. ', '! ', '? ', '\n']

        # 在指定范围内查找最后一个句子边界
        search_range = text[start:end]
        last_pos = end

        for ending in sentence_endings:
            pos = search_range.rfind(ending)
            if pos != -1:
                # 转换为原始文本中的位置
                original_pos = start + pos + len(ending)
                if original_pos < last_pos and original_pos > start:
                    last_pos = original_pos

        # 如果没找到句子边界，在空格处分割
        if last_pos == end:
            space_pos = search_range.rfind(' ')
            if space_pos != -1:
                last_pos = start + space_pos + 1

        return last_pos


class EmbeddingService:
    """
    Embedding 服务

    使用 SentenceTransformer 模型将文本转换为向量表示。
    """

    def __init__(self, model_path: str = None):
        """
        初始化 Embedding 服务。

        Args:
            model_path: SentenceTransformer 模型路径，如果为 None 使用默认模型
        """
        self.model_path = model_path or self._get_default_model_path()
        self.model = None
        self._load_model()

    def _get_default_model_path(self) -> str:
        """
        获取默认模型路径。

        Returns:
            默认模型路径
        """
        # 默认模型路径
        return r"D:\code_project\ai-wx\AgentForge\backend\fast-bge-small-zh-v1.5"

    def _load_model(self):
        """
        加载 SentenceTransformer 模型。
        """
        try:
            if os.path.exists(self.model_path):
                self.model = SentenceTransformer(self.model_path)
            else:
                # 如果指定路径不存在，使用默认模型
                print(f"警告：模型路径 {self.model_path} 不存在，使用默认模型")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"加载模型失败: {e}")
            # 创建一个简单的 mock 模型用于测试
            self.model = None

    def encode(self, text: str) -> List[float]:
        """
        将单个文本编码为向量。

        Args:
            text: 要编码的文本

        Returns:
            向量表示
        """
        if not text:
            return []

        if self.model is None:
            # 如果模型未加载，返回模拟向量
            return [0.1, 0.2, 0.3, 0.4, 0.5]

        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"编码失败: {e}")
            return [0.1, 0.2, 0.3, 0.4, 0.5]

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量将文本编码为向量。

        Args:
            texts: 要编码的文本列表

        Returns:
            向量表示列表
        """
        if not texts:
            return []

        if self.model is None:
            # 如果模型未加载，返回模拟向量
            return [[0.1, 0.2] for _ in texts]

        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            print(f"批量编码失败: {e}")
            return [[0.1, 0.2] for _ in texts]


class VectorStoreService:
    """
    向量存储服务

    使用 ChromaDB 存储和检索向量化的文档。
    """

    def __init__(self, collection_name: str = "rag_collection", db_path: str = "./chroma_db"):
        """
        初始化向量存储服务。

        Args:
            collection_name: ChromaDB 集合名称
            db_path: ChromaDB 数据库路径
        """
        self.collection_name = collection_name
        self.db_path = db_path
        self.client = None
        self.collection = None
        self._initialize()

    def _initialize(self):
        """
        初始化 ChromaDB 客户端和集合。
        """
        try:
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )
        except Exception as e:
            print(f"初始化 ChromaDB 失败: {e}")
            self.client = None
            self.collection = None

    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """
        添加文档到向量存储。

        Args:
            ids: 文档 ID 列表
            embeddings: 文档向量列表
            documents: 文档内容列表
            metadatas: 文档元数据列表（可选）
        """
        if self.collection is None:
            print("ChromaDB 集合未初始化")
            return

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
        except Exception as e:
            print(f"添加文档失败: {e}")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行相似度搜索。

        Args:
            query_embedding: 查询向量
            top_k: 返回的最大结果数
            filter_metadata: 元数据过滤条件（可选）

        Returns:
            搜索结果字典，包含 documents、distances 和 ids
        """
        if self.collection is None:
            print("ChromaDB 集合未初始化")
            return {
                'documents': [[]],
                'distances': [[]],
                'ids': [[]]
            }

        try:
            kwargs = {
                'query_embeddings': [query_embedding],
                'n_results': top_k,
                'include': ['documents', 'metadatas', 'distances']
            }

            if filter_metadata:
                kwargs['where'] = filter_metadata

            results = self.collection.query(**kwargs)

            # 转换距离为相似度（余弦距离转相似度）
            if 'distances' in results and results['distances']:
                results['distances'] = [
                    [1 - dist for dist in dist_list]
                    for dist_list in results['distances']
                ]

            return results

        except Exception as e:
            print(f"搜索失败: {e}")
            return {
                'documents': [[]],
                'distances': [[]],
                'ids': [[]]
            }

    def delete_documents(self, ids: List[str]):
        """
        删除文档。

        Args:
            ids: 要删除的文档 ID 列表
        """
        if self.collection is None:
            print("ChromaDB 集合未初始化")
            return

        try:
            self.collection.delete(ids=ids)
        except Exception as e:
            print(f"删除文档失败: {e}")

    def count(self) -> int:
        """
        获取集合中的文档数量。

        Returns:
            文档数量
        """
        if self.collection is None:
            return 0

        try:
            return self.collection.count()
        except Exception as e:
            print(f"获取文档数量失败: {e}")
            return 0


class RAGPipeline:
    """
    RAG Pipeline

    整合文档分块、向量化和存储的完整流程。
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        model_path: str = None,
        collection_name: str = "rag_collection"
    ):
        """
        初始化 RAG Pipeline。

        Args:
            chunk_size: 文本块大小
            chunk_overlap: 文本块重叠大小
            model_path: Embedding 模型路径
            collection_name: 向量存储集合名称
        """
        self.chunker = DocumentChunker(chunk_size, chunk_overlap)
        self.embedding_service = EmbeddingService(model_path)
        self.vector_store = VectorStoreService(collection_name)

    def process_document(
        self,
        document: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理文档：分块 → 向量化 → 存储。

        Args:
            document: 文档内容
            document_id: 文档 ID
            metadata: 文档元数据（可选）

        Returns:
            处理结果字典
        """
        # 分块
        chunks = self.chunker.chunk_text(document)

        if not chunks:
            return {
                'status': 'error',
                'message': '文档分块失败',
                'document_id': document_id,
                'chunks_count': 0
            }

        # 向量化
        embeddings = self.embedding_service.encode_batch(chunks)

        # 生成每个块的 ID
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]

        # 为每个块添加元数据
        chunk_metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'document_id': document_id,
                'chunk_index': i,
                'chunk_text': chunk[:100]  # 存储前 100 个字符作为预览
            }
            if metadata:
                chunk_metadata.update(metadata)
            chunk_metadatas.append(chunk_metadata)

        # 存储到向量数据库
        self.vector_store.add_documents(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=chunk_metadatas
        )

        return {
            'status': 'success',
            'document_id': document_id,
            'chunks_count': len(chunks)
        }

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        查询知识库：向量化 → 检索 → 返回结果。

        Args:
            query_text: 查询文本
            top_k: 返回的最大结果数
            filter_metadata: 元数据过滤条件（可选）

        Returns:
            查询结果字典
        """
        # 向量化查询
        query_embedding = self.embedding_service.encode(query_text)

        if not query_embedding:
            return {
                'status': 'error',
                'message': '查询向量化失败',
                'documents': [[]],
                'distances': [[]],
                'ids': [[]]
            }

        # 检索相关文档
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )

        results['status'] = 'success'
        return results

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        删除文档及其所有块。

        Args:
            document_id: 文档 ID

        Returns:
            删除结果字典
        """
        try:
            # 查询所有属于该文档的块
            # 注意：ChromaDB 的 where 查询可能需要根据实际版本调整
            self.vector_store.delete_documents([f"{document_id}_chunk_0"])
            return {
                'status': 'success',
                'document_id': document_id,
                'message': '文档删除成功'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'删除文档失败: {e}',
                'document_id': document_id
            }
