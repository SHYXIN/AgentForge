"""
知识库文档数据种子模块

创建测试知识库文档。
"""
import sys
import os

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.services.rag import RAGPipeline


async def seed_rag_documents(clean: bool = True):
    """创建知识库文档数据。

    Args:
        clean: 是否清理旧数据
    """
    rag_pipeline = RAGPipeline()

    if clean:
        print("清理旧知识库文档数据...")

    # 创建测试知识库文档
    test_documents = [
        {
            "id": "doc-001",
            "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by humans or animals.",
            "metadata": {"source": "wikipedia", "category": "AI"}
        },
        {
            "id": "doc-002",
            "text": "Machine learning is a branch of artificial intelligence (AI) and computer science which focuses on the use of data and algorithms to imitate the way that humans learn.",
            "metadata": {"source": "wikipedia", "category": "ML"}
        },
        {
            "id": "doc-003",
            "text": "Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language.",
            "metadata": {"source": "wikipedia", "category": "NLP"}
        }
    ]

    for doc_data in test_documents:
        try:
            result = rag_pipeline.process_document(
                document=doc_data["text"],
                document_id=doc_data["id"],
                metadata=doc_data["metadata"]
            )
            if result.get("status") == "success":
                print(f"知识库文档创建成功: {doc_data['id']} (chunks: {result.get('chunks_count', 0)})")
            else:
                print(f"知识库文档创建失败 {doc_data['id']}: {result.get('message', 'unknown error')}")
        except Exception as e:
            print(f"知识库文档创建失败 {doc_data['id']}: {e}")

    print(f"知识库文档数据种子完成")
