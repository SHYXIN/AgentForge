"""
Embedding 服务模块

使用 ONNX 格式的 BGE 模型进行文本向量化。
"""
import os
import numpy as np
from tokenizers import Tokenizer
import onnxruntime as ort


class LocalBGEEmbedding:
    """本地 BGE Embedding（ONNX 格式）"""

    def __init__(self, model_dir: str = None):
        """
        初始化 BGE Embedding。

        Args:
            model_dir: 模型目录路径
        """
        if model_dir is None:
            model_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "fast-bge-small-zh-v1.5"
            )

        # 使用教程中的模型路径结构
        model_path = os.path.join(model_dir, "fast-bge-small-zh-v1.5")
        if not os.path.exists(model_path):
            # 如果不存在，尝试直接使用 model_dir
            model_path = model_dir

        self.tokenizer = Tokenizer.from_file(os.path.join(model_path, "tokenizer.json"))
        self.session = ort.InferenceSession(
            os.path.join(model_path, "model_optimized.onnx"),
            providers=["CPUExecutionProvider"]
        )
        print(f"[EMBEDDING] 加载 BGE 模型: {model_path}")

    def _embed(self, texts):
        """向量化文本"""
        encoded = self.tokenizer.encode_batch(texts)
        max_len = max(len(e.ids) for e in encoded)
        max_len = min(max_len, 256)  # 限制最大序列长度

        input_ids = np.zeros((len(encoded), max_len), dtype=np.int64)
        attention_mask = np.zeros((len(encoded), max_len), dtype=np.int64)
        token_type_ids = np.zeros((len(encoded), max_len), dtype=np.int64)

        for i, e in enumerate(encoded):
            ids = e.ids[:max_len]
            mask = e.attention_mask[:max_len]
            types = e.type_ids[:max_len]
            input_ids[i, :len(ids)] = ids
            attention_mask[i, :len(mask)] = mask
            token_type_ids[i, :len(types)] = types

        outputs = self.session.run(None, {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids
        })

        last_hidden_state = outputs[0]
        mask_expanded = np.expand_dims(attention_mask, -1)
        sum_embeddings = np.sum(last_hidden_state * mask_expanded, axis=1)
        sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
        embeddings = sum_embeddings / sum_mask
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / np.clip(norms, a_min=1e-9, a_max=None)

    def embed_documents(self, texts):
        """向量化文档列表"""
        return self._embed(texts).tolist()

    def embed_query(self, text):
        """向量化单个查询"""
        return self._embed([text])[0].tolist()
