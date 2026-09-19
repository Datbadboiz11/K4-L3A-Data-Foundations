from __future__ import annotations

from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        """
        Retrieve relevant chunks from store and prompt the LLM to answer.
        """
        if self.store.get_collection_size() == 0:
            return "Kho tri thức hiện chưa có tài liệu nào."

        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong kho tri thức để trả lời."

        context_blocks: list[str] = []
        for idx, r in enumerate(results, start=1):
            source = (
                r.get("metadata", {}).get("source_url")
                or r.get("metadata", {}).get("source")
                or r.get("id", f"doc_{idx}")
            )
            context_blocks.append(f"[{idx}] (Nguồn: {source})\n{r['content']}")

        context_str = "\n\n".join(context_blocks)

        prompt = (
            "Bạn là trợ lý giải đáp thông tin học vụ và quy chế đại học.\n"
            "Hãy trả lời câu hỏi dưới đây DỰA HOÀN TOÀN vào các đoạn ngữ cảnh được cung cấp.\n"
            "Yêu cầu:\n"
            "- Trích dẫn số thứ tự nguồn [1], [2] tương ứng với thông tin bạn sử dụng.\n"
            "- Nếu thông tin không có trong ngữ cảnh, hãy trả lời rõ ràng là không tìm thấy, không tự suy diễn.\n\n"
            f"=== NGỮ CẢNH ===\n{context_str}\n\n"
            f"=== CÂU HỎI ===\n{question}\n\n"
            "=== CÂU TRẢ LỜI ==="
        )
        return self.llm_fn(prompt)
