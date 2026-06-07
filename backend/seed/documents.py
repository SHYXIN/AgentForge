"""
文档数据种子模块

创建测试文档。
"""
import sys
import os

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.repositories.memory import InMemoryDocumentRepository


async def seed_documents(clean: bool = True):
    """创建文档数据。

    Args:
        clean: 是否清理旧数据
    """
    doc_repo = InMemoryDocumentRepository()

    if clean:
        print("清理旧文档数据...")
        # 清理现有文档
        doc_repo.documents.clear()

    # 创建测试文档
    test_documents = [
        {
            "filename": "readme.txt",
            "content_type": "text/plain",
            "content": b"Welcome to AgentForge!\n\nThis is a test document for the RAG system."
        },
        {
            "filename": "guide.md",
            "content_type": "text/markdown",
            "content": b"# AgentForge Guide\n\n## Getting Started\n\nThis is a test markdown document."
        },
        {
            "filename": "notes.txt",
            "content_type": "text/plain",
            "content": b"Test notes for the document management system.\n\n- Note 1\n- Note 2\n- Note 3"
        }
    ]

    for doc_data in test_documents:
        try:
            doc = await doc_repo.create(
                filename=doc_data["filename"],
                content_type=doc_data["content_type"],
                content=doc_data["content"]
            )
            print(f"文档创建成功: {doc.filename} (ID: {doc.id})")
        except Exception as e:
            print(f"文档创建失败 {doc_data['filename']}: {e}")

    print(f"文档数据种子完成")
