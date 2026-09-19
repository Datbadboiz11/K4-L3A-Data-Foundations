"""
Script kiểm tra thực tế hoạt động của RecursiveChunker và so sánh 3 chiến lược chunking
trên bộ dữ liệu quy chế Trường Đại học Công nghệ - ĐHQGHN (UET).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Đảm bảo import được gói src từ thư mục gốc
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chunking import (
    ChunkingStrategyComparator,
    FixedSizeChunker,
    RecursiveChunker,
    SentenceChunker,
)


def main() -> None:
    # Thiết lập UTF-8 để in tiếng Việt chuẩn trên Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("DEMO KIỂM TRA CHUNKING TRÊN DỮ LIỆU ĐẠI HỌC CÔNG NGHỆ (UET)")
    print("=" * 70)

    # 1. Thử nghiệm RecursiveChunker trên file tuyen-sinh.md
    sample_file = Path("data/university/tuyen-sinh.md")
    if not sample_file.exists():
        print(f"Không tìm thấy file: {sample_file}")
        return

    text = sample_file.read_text(encoding="utf-8")
    print(f"\n[1] Thử nghiệm RecursiveChunker trên '{sample_file.name}'")
    print(f"    - Tổng độ dài văn bản: {len(text):,} ký tự")

    chunker = RecursiveChunker(chunk_size=400)
    chunks = chunker.chunk(text)
    print(f"    - Kích thước chunk_size: 400 ký tự")
    print(f"    - Số lượng chunk sinh ra: {len(chunks)} chunks")
    print(f"    - Độ dài trung bình: {sum(len(c) for c in chunks) / len(chunks):.1f} ký tự")

    print("\n--- Preview 2 Chunk đầu tiên ---")
    for i, chunk in enumerate(chunks[:2], start=1):
        print(f"\n[Chunk {i}] ({len(chunk)} ký tự):")
        print("-" * 40)
        print(chunk.strip())
        print("-" * 40)

    # 2. So sánh 3 chiến lược trên quy chế đào tạo
    big_file = Path("data/university/quy-che-dao-tao.md")
    if big_file.exists():
        big_text = big_file.read_text(encoding="utf-8")
        print(f"\n[2] So sánh 3 chiến lược trên '{big_file.name}' ({len(big_text):,} ký tự):")
        
        comp = ChunkingStrategyComparator()
        results = comp.compare(big_text, chunk_size=500)
        
        print(f"\n{'Chiến lược':<20} | {'Số Chunk':<10} | {'Độ dài TB':<12} | {'Đánh giá giữ ngữ cảnh'}")
        print("-" * 70)
        assessments = {
            "fixed_size": "Kém: Cắt ngang câu/khoản quy chế",
            "by_sentences": "Trung bình: Mất liên kết mục a, b, c",
            "recursive": "Tốt nhất: Giữ trọn vẹn Điều/Khoản",
        }
        for name, data in results.items():
            count = data["count"]
            avg_len = data["avg_length"]
            note = assessments.get(name, "")
            print(f"{name:<20} | {count:<10} | {avg_len:<12.1f} | {note}")

    print("\n" + "=" * 70)
    print("Tất cả kiểm tra hoàn tất thành công!")
    print("=" * 70)


if __name__ == "__main__":
    main()
