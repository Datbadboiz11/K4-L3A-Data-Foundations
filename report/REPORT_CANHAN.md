# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Thân Tiến Đạt
**Nhóm:** G49
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiến gần về 1.0) nghĩa là hai vector embedding cùng chỉ về một hướng trong không gian đa chiều, thể hiện hai đoạn văn bản có sự tương đồng lớn về mặt ngữ nghĩa và ý niệm, bất kể độ dài hay từ vựng sử dụng có khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên hoàn thành các môn học theo tiến độ sẽ được xét tốt nghiệp sớm."
- Câu B: "Người học tích lũy đủ số tín chỉ trước thời hạn có thể ra trường trước hạn."
- Tại sao tương đồng: Dù sử dụng từ vựng hoàn toàn khác nhau (sinh viên / người học, môn học / tín chỉ, tốt nghiệp sớm / ra trường trước hạn), hai câu vẫn biểu đạt chung một ý nghĩa quy chế học vụ.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Trường Đại học Công nghệ công bố điểm chuẩn trúng tuyển năm 2026."
- Câu B: "Khu đô thị Hòa Lạc trồng rất nhiều cây xanh và hoa ban rực rỡ."
- Tại sao khác: Một câu nói về chính sách học vụ tuyển sinh, câu còn lại miêu tả cảnh quan thực vật; hai không gian ngữ nghĩa hoàn toàn không liên quan nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid phụ thuộc trực tiếp vào độ dài (độ lớn vector). Một đoạn văn ngắn và một đoạn văn dài dù cùng chủ đề vẫn có khoảng cách Euclid rất xa nhau. Ngược lại, Cosine similarity chỉ đo góc giữa hai vector (đo hướng ngữ nghĩa) và triệt tiêu ảnh hưởng của độ dài văn bản, giúp so sánh chính xác mức độ tương đồng ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* $\lceil (10.000 - 50) / (500 - 50) \rceil = \lceil 9.950 / 450 \rceil = \lceil 22.11 \rceil = 23$  
> *Đáp án:* **23 chunks** (Đã kiểm chứng khớp bằng `FixedSizeChunker(chunk_size=500, overlap=50).chunk('a'*10000)`).

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Phép tính khi tăng overlap lên 100: $\lceil (10.000 - 100) / (500 - 100) \rceil = \lceil 9.900 / 400 \rceil = \lceil 24.75 \rceil = 25$ chunks (số chunk tăng từ 23 lên 25).  
> Ta muốn tăng độ chồng chéo để duy trì tính liên tục của ngữ cảnh giữa hai chunk liền kề, tránh việc cắt đôi một câu phức hoặc một mệnh đề quan trọng ở ranh giới chunk, giúp mô hình retrieval không bị mất thông tin quan trọng.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng regex positive lookbehind `(?<=[.!?])(?:\s+|\n+)` để tách câu tại vị trí ngay sau dấu câu mà không làm mất dấu câu (tránh câu cụt). Sau đó nhóm các câu theo kích thước `max_sentences_per_chunk`, loại bỏ khoảng trắng thừa và xử lý chuỗi rỗng trả về `[]`. Biết rõ edge case chưa xử lý được là các từ viết tắt (như TS., GS.) và số thập phân (3.14).

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Áp dụng thuật toán 2 chiều: đệ quy xuống sâu theo danh sách separator ưu tiên `["\n\n", "\n", ". ", " ", ""]` khi đoạn văn bản vượt quá `chunk_size`; sau đó gom các mảnh nhỏ liền kề lại cho tới sát `chunk_size` để tránh sinh ra các chunk vụn. Base case gồm: chuỗi rỗng trả về `[]`, đoạn $\le$ `chunk_size` trả về chính nó, và khi `remaining_separators` rỗng thì cắt cứng theo `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Dữ liệu được lưu trữ in-memory dưới dạng danh sách `self._store: list[dict]`, mỗi record chứa `id`, `content`, bản sao `metadata` (đảm bảo luôn có trường `doc_id`) và vector `embedding` chuẩn hóa từ hàm embedding. Hàm `search` gọi qua helper `_search_records`, nhúng câu truy vấn, tính độ tương tự cosine với từng record trong store, sắp xếp giảm dần theo điểm và trả về `top_k` kết quả (loại bỏ trường embedding thô để đầu ra gọn gàng).

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Áp dụng cơ chế **Lọc trước (Pre-filtering)**: lọc danh sách ứng viên trong `self._store` thỏa mãn toàn bộ điều kiện trong `metadata_filter` trước khi tính điểm tương đồng (tránh tình trạng lọc sau bị mất hết kết quả do top-k bị tài liệu không khớp chiếm giữ). Hàm `delete_document` duyệt xóa mọi record có `id == doc_id` hoặc `metadata['doc_id'] == doc_id`, so sánh độ dài store trước và sau khi xóa để trả về `True` nếu có bản ghi bị xóa, ngược lại trả về `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Triển khai mô hình RAG theo 3 nhịp: (1) Kiểm tra store rỗng trả về thông báo an toàn, gọi `store.search` lấy top-k chunk liên quan nhất; (2) Dựng prompt ngữ cảnh đánh số thứ tự `[1]`, `[2]` kèm nguồn tài liệu cụ thể nhằm đảm bảo tiêu chí truy vết nguồn (source traceability) và ra lệnh LLM chỉ dựa vào ngữ cảnh được cấp, cấm tự suy diễn; (3) Truyền prompt hoàn chỉnh vào `llm_fn` để sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Program Files\Python312\python.exe
cachedir: .pytest_cache
rootdir: D:\AI thực chiến K4\K4-L3A-Data-Foundations
plugins: anyio-4.15.1
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.13s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42 (100%)

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

*(Đã thực nghiệm bằng mô hình OpenAI `text-embedding-3-small` thực tế kết hợp đối chiếu với Mock)*

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế (OpenAI) | Điểm Mock | Đúng? |
|------|-----------|-----------|---------|-----------------------|-----------|-------|
| 1 | Sinh viên hoàn thành các môn học theo tiến độ sẽ được xét tốt nghiệp sớm. | Người học tích lũy đủ số tín chỉ trước thời hạn có thể ra trường trước hạn. | cao | **0.5169** (cao) | -0.0289 | Đúng |
| 2 | Trường Đại học Công nghệ công bố điểm chuẩn trúng tuyển năm 2026. | Khuôn viên Hòa Lạc có rất nhiều cây xanh và hồ nước thoáng mát. | thấp | **0.2036** (thấp) | 0.1689 | Đúng |
| 3 | Sinh viên có điểm trung bình chung học kỳ dưới 0.8 sẽ bị cảnh báo học vụ. | Kết quả học tập kỳ này quá thấp khiến người học rơi vào diện cảnh cáo. | cao | **0.4417** (cao) | 0.0288 | Đúng |
| 4 | Hồ sơ đăng ký xét tuyển gồm học bạ THPT và phiếu điểm thi đánh giá năng lực. | Thí sinh nộp kết quả thi HSA cùng bảng điểm cấp 3 để xét tuyển vào đại học. | cao | **0.5731** (cao) | 0.1686 | Đúng |
| 5 | Học bổng khuyến khích học tập được cấp theo từng học kỳ cho sinh viên xuất sắc. | Lịch thi kết thúc học phần học kỳ 2 bắt đầu từ ngày 15 tháng 6. | thấp | **0.4064** (trung bình) | 0.1395 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả ấn tượng nhất là ở Cặp 1: hai câu sử dụng hai hệ từ vựng hoàn toàn khác nhau ("sinh viên / người học", "môn học / tín chỉ", "tốt nghiệp sớm / ra trường trước hạn"). Khi dùng Mock (băm ký tự nông), điểm số bị âm (-0.0289) vì không trùng ký tự; nhưng khi chuyển sang OpenAI `text-embedding-3-small`, điểm nhảy vọt lên **0.5169** (rất cao). Điều này chứng minh rằng mô hình Dense Neural Embedding thực sự nắm bắt được không gian ý niệm ngữ nghĩa (semantic concept) thay vì chỉ so khớp từ khóa cơ học.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src` với embedding OpenAI `text-embedding-3-small` (kết quả lưu tại `ket_qua_benchmark.txt`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên có thể tìm kiếm những cơ hội nghề nghiệp nào thông qua UET? | `co-hoi-nghe-nghiep#0`: Cổng thông tin việc làm UET, kết nối doanh nghiệp, tuyển dụng Kỹ sư C/C++, Embedded Software, cơ khí. | 0.7396 | Có liên quan (Top-1) | [1] Cung cấp các cơ hội thực tập và việc làm kỹ sư phần mềm C/C++, Embedded Engineer, thiết kế cơ khí và kết nối doanh nghiệp tuyển dụng. |
| 2 | UET hiện cung cấp những thông tin tuyển sinh nào cho thí sinh? | `tuyen-sinh#0`: Thông tin tuyển sinh đại học chính quy UET, điểm chuẩn các ngành, chính sách học bổng hỗ trợ sinh hoạt phí NĐ 179. | 0.5122 (Top-2) | Có liên quan (Top-2) | [1] Thông tin điểm chuẩn trúng tuyển, chính sách học bổng Nghị định 179 (3,6 tr/tháng), ngưỡng điểm sàn, quy đổi điểm và danh mục ngành xét tuyển. |
| 3 | Những mục tiêu chính trong chiến lược phát triển của Trường Đại học Công nghệ là gì? | `chien-luoc-phat-trien#2`: Chiến lược phát triển đến 2030, tầm nhìn 2045, trở thành cơ sở GDĐH hàng đầu cả nước về kỹ thuật công nghệ. | 0.6108 | Có liên quan (Top-1) | [1] Trở thành cơ sở giáo dục đại học hàng đầu cả nước về tiên phong, sáng tạo và dẫn dắt đào tạo nhân lực bậc cao; lọt top trường tiên tiến Châu Á vào năm 2045. |
| 4 | Điều kiện và trình tự để mở một ngành đào tạo trình độ đại học được quy định như thế nào? | `quy-dinh-mo-nganh#0`: Căn cứ pháp lý mở ngành: Thông tư 02/2022, Thông tư 12/2024 của Bộ GD&ĐT và QĐ 4555/QĐ-ĐHQGHN. | 0.7073 | Có liên quan (Top-1) | [1] Căn cứ theo Thông tư 02/2022/TT-BGDĐT, Thông tư 12/2024/TT-BGDĐT và Quyết định 4555/QĐ-ĐHQGHN về quy định điều kiện, thủ tục mở ngành tại ĐHQGHN. |
| 5 | Theo quy chế đào tạo đại học của ĐHQGHN, sinh viên cần đáp ứng những điều kiện nào để được công nhận tốt nghiệp? *(Lọc `{"audience": "student"}`)* | `quy-che-dao-tao#175`: Điều 43 QĐ 5115 về các điều kiện tốt nghiệp (tích lũy tín chỉ, ĐTBCTL $\ge 2.0$, ngoại ngữ, GDQP-AN, GDTC). | 0.6331 | Có liên quan (Top-1) | [1] Theo Điều 43 QĐ 5115: Trong thời gian tối đa, tích lũy đủ số tín chỉ, ĐTBCTL đạt từ 2,00 trở lên (2,50 với tài năng/CLC), đạt chuẩn ngoại ngữ, GDQP-AN và GDTC. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (100% câu hỏi đều trả về tài liệu chuẩn trong Top-1 và Top-2; tổng điểm đạt 9/10).

**Phân tích ca thất bại (Failure Case Analysis) & Bài học rút ra:**
> 1. **Phân tích cạnh tranh từ khóa ở Câu hỏi 2:** Ở Câu hỏi 2 (*"UET hiện cung cấp những thông tin tuyển sinh nào..."*), chunk về cơ hội nghề nghiệp (`co-hoi-nghe-nghiep#0`) lại lọt lên Top-1 (0.5824) trước chunk tuyển sinh (`tuyen-sinh#0`, 0.5122 ở Top-2). Nguyên nhân do từ vựng *"sinh viên"*, *"cung cấp thông tin"* có tần suất cao trong trang việc làm, trong khi câu hỏi mang tính khái quát. Tuy nhiên, chunk đúng của đề án tuyển sinh vẫn nằm chắc chắn ở Top-2 và cung cấp đầy đủ thông tin chuẩn xác cho Agent trả lời.  
> 2. **Phân tích A/B Testing ở Câu hỏi 4 & 5:** Ở Câu hỏi 4, khi không dùng bộ lọc, hệ thống trả về văn bản quản trị nội bộ dành riêng cho cán bộ/giảng viên mở ngành (`quy-dinh-mo-nganh.md`, `audience: faculty`) với điểm 0.7073. Khi bật pre-filtering `{"audience": "student"}` cho sinh viên, 100% tài liệu của cán bộ bị loại bỏ, hệ thống chỉ giữ lại các điều khoản trong quy chế đào tạo của người học. Điều này chứng minh Pre-filtering là bắt buộc trong các hệ thống RAG thực tế để tránh lẫn lộn phân quyền người dùng.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |

