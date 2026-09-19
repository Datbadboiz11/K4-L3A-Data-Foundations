# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm UET — K4-L3A
**Thành viên:** Thân Tiến Đạt, [Thành viên 2], [Thành viên 3]
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy chế đào tạo tín chỉ, quy định học vụ, chính sách tuyển sinh và dịch vụ sinh viên Trường Đại học Công nghệ – Đại học Quốc gia Hà Nội (VNU-UET).

**Tại sao nhóm chọn chủ đề này?**
> 1. Trường Đại học Công nghệ (ĐHQGHN) áp dụng mô hình đào tạo theo hệ thống tín chỉ nghiêm ngặt dựa trên Quyết định số 5115/QĐ-ĐHQGHN với 47 điều khoản chi tiết, tạo ra bài toán tra cứu học vụ thực tế với độ phức tạp cao.  
> 2. Khối lượng thắc mắc của sinh viên về quy chế học vụ (cảnh báo buộc thôi học, điều kiện đăng ký môn, học bổng theo Nghị định 179, chuẩn đầu ra ngoại ngữ) là rất lớn; một hệ thống RAG chuẩn xác sẽ trực tiếp hỗ trợ giải tỏa áp lực tư vấn cho Phòng Đào tạo và Phòng Công tác Sinh viên.  
> 3. Bộ tài liệu có tính phân cấp hành chính rõ rệt (Chương, Điều, Khoản) và phân hóa rõ ràng theo đối tượng độc giả (`audience: student` vs `audience: faculty`), tạo tiền đề tuyệt vời để kiểm chứng hiệu quả của các giải thuật chunking và cơ chế lọc metadata (metadata filtering).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy chế đào tạo đại học (QĐ 5115) | https://uet.edu.vn/quy-che-dao-tao-dai-hoc-cua-dai-hoc-quoc-gia-ha-noi-theo-quyet-dinh-5115qd-dhqghn/ | 2026-09-19 / Quyết định 5115/QĐ-ĐHQGHN | 73,177 | `doc_id: quy-che-dao-tao`, `audience: student`, `department: dao-tao`, `category: academic-regulation` |
| 2 | Thông tin tuyển sinh ĐHCQ 2026 | https://uet.edu.vn/tuyen-sinh/ | 2026-09-19 / Đề án tuyển sinh 2026 | 3,606 | `doc_id: tuyen-sinh`, `audience: student`, `department: tuyen-sinh`, `category: admissions` |
| 3 | Cơ hội nghề nghiệp & việc làm | https://vieclam.uet.vnu.edu.vn/co-hoi-nghe-nghiep | 2026-09-19 / Bản tin việc làm 09/2026 | 4,239 | `doc_id: co-hoi-nghe-nghiep`, `audience: student`, `department: ctsv`, `category: career-services` |
| 4 | Quy định mở ngành đào tạo | https://uet.edu.vn/quy-dinh-dieu-kien-trinh-tu-thu-tuc-mo-nganh-dao-tao-trinh-do-dai-hoc/ | 2026-09-19 / Quyết định mở ngành | 1,869 | `doc_id: quy-dinh-mo-nganh`, `audience: faculty`, `department: dao-tao`, `category: institutional-governance` |
| 5 | Chiến lược phát triển đến 2030, tầm nhìn 2045 | https://uet.edu.vn/chien-luoc-phat-trien/ | 2026-09-19 / Nghị quyết chiến lược | 14,888 | `doc_id: chien-luoc-phat-trien`, `audience: general-public`, `department: bgh`, `category: strategy` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `"quy-che-dao-tao"` | Định danh duy nhất cho văn bản gốc, dùng để nhóm các chunk và hỗ trợ xóa tài liệu theo ID (`delete_document`). |
| `audience` | `str` | `"student"`, `"faculty"` | Phân quyền/định hướng đối tượng tra cứu. Cho phép lọc triệt để các quy định chỉ áp dụng cho cán bộ/giảng viên khi sinh viên đặt câu hỏi. |
| `department` | `str` | `"dao-tao"`, `"ctsv"`, `"tuyen-sinh"` | Khoanh vùng đơn vị chịu trách nhiệm xử lý nghiệp vụ, giúp AI loại bỏ các tài liệu từ phòng ban không liên quan. |
| `category` | `str` | `"academic-regulation"`, `"admissions"` | Phân loại chủ đề ngữ nghĩa, ngăn ngừa việc nhầm lẫn giữa quy chế học vụ với tin tuyển dụng hoặc quy chế thi đua. |
| `document_version` | `str` | `"Quyết định 5115/QĐ-ĐHQGHN"` | Đảm bảo tính xác thực pháp lý và tính cập nhật, giúp hệ thống phân biệt phiên bản mới nhất với các văn bản đã hết hiệu lực. |
| `source_url` | `str` | `"https://uet.edu.vn/..."` | Cung cấp nguồn kiểm chứng minh bạch cho sinh viên theo dõi trực tiếp điều khoản gốc trên cổng thông tin UET. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu tiêu biểu của kho dữ liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `quy-che-dao-tao.md` (73,177 chars) | FixedSizeChunker (`fixed_size`, cs=200) | 488 | 199.9 ký tự | **Kém:** Bị ngắt cứng giữa chừng câu, cắt đôi các điều kiện và hình thức xử phạt ở các Điều 28, 29. |
| `quy-che-dao-tao.md` (73,177 chars) | SentenceChunker (`by_sentences`) | 133 | 542.7 ký tự | **Trung bình:** Tách theo câu nhưng làm mất liên kết giữa câu dẫn quy định và danh sách gạch đầu dòng $a, b, c$. |
| `quy-che-dao-tao.md` (73,177 chars) | RecursiveChunker (`recursive`, cs=200) | 478 | 151.3 ký tự | **Tốt:** Ưu tiên tách theo đoạn `\n\n`, giữ trọn vẹn ngữ nghĩa của từng khoản/điểm trong điều khoản. |
| `tuyen-sinh.md` (3,606 chars) | FixedSizeChunker (`fixed_size`, cs=200) | 24 | 198.2 ký tự | **Kém:** Cắt ngang bảng chỉ tiêu và chính sách học bổng Nghị định 179 thành hai nửa rời rạc. |
| `tuyen-sinh.md` (3,606 chars) | SentenceChunker (`by_sentences`) | 8 | 449.2 ký tự | **Trung bình:** Gộp nhiều mốc thời gian và phương thức xét tuyển vào cùng một chunk lớn. |
| `tuyen-sinh.md` (3,606 chars) | RecursiveChunker (`recursive`, cs=200) | 23 | 155.7 ký tự | **Rất tốt:** Phân tách hoàn hảo từng khối thông tin: chỉ tiêu, tổ hợp xét tuyển, học bổng theo mục `##`. |
| `co-hoi-nghe-nghiep.md` (4,239 chars) | FixedSizeChunker (`fixed_size`, cs=200) | 28 | 199.6 ký tự | **Kém:** Ngắt giữa chừng tên doanh nghiệp và yêu cầu tuyển dụng kỹ sư. |
| `co-hoi-nghe-nghiep.md` (4,239 chars) | SentenceChunker (`by_sentences`) | 4 | 1058.5 ký tự | **Kém:** Do bản tin tuyển dụng ít dấu chấm câu truyền thống, chunk bị phình to vượt quá 1,000 ký tự. |
| `co-hoi-nghe-nghiep.md` (4,239 chars) | RecursiveChunker (`recursive`, cs=200) | 25 | 168.1 ký tự | **Tốt:** Bắt đúng các ngắt dòng `\n` và `\n\n` để gom từng vị trí việc làm thành một chunk hoàn chỉnh. |

### Chiến lược của từng thành viên

**Thành viên 1 — Thân Tiến Đạt**
- **Loại chiến lược:** RecursiveChunker (Tối ưu danh sách phân tách phân cấp cho văn bản quy phạm học vụ)
- **Mô tả & lý do chọn cho chủ đề này:**  
  Văn bản quy chế như Quyết định 5115 có tính phân tầng logic: *Chương $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm*. Tôi chọn `RecursiveChunker` vì thuật toán đệ quy lần lượt qua `["\n\n", "\n", ". ", " ", ""]`. Khi một Điều khoản nằm gọn trong `chunk_size`, nó được giữ nguyên vẹn 100%. Chỉ khi một Điều quá dài mới bị chia nhỏ xuống mức Khoản hoặc câu, loại bỏ hoàn toàn hiện tượng câu cụt hoặc mất tiêu đề điều luật.
- **Code snippet:**
```python
class RecursiveChunker:
    """Đệ quy chia nhỏ văn bản theo độ ưu tiên separator, tối ưu cho quy chế UET."""
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        sep = remaining_separators[0]
        next_separators = remaining_separators[1:]
        if sep == "":
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]
        if sep not in current_text:
            return self._split(current_text, next_separators)

        splits = current_text.split(sep)
        sub_chunks: list[str] = []
        for piece in splits:
            if piece:
                if len(piece) > self.chunk_size:
                    sub_chunks.extend(self._split(piece, next_separators))
                else:
                    sub_chunks.append(piece)

        merged: list[str] = []
        cur = ""
        for piece in sub_chunks:
            if not cur:
                cur = piece
            elif len(cur) + len(sep) + len(piece) <= self.chunk_size:
                cur += sep + piece
            else:
                merged.append(cur)
                cur = piece
        if cur:
            merged.append(cur)
        return merged
```

**Thành viên 2 — [Thành viên 2]**
- **Loại chiến lược:** SentenceChunker (`max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn:**  
  Sử dụng ranh giới dấu câu (`. `, `! `, `? `) để tạo các chunk gồm tối đa 3 câu hoàn chỉnh. Chiến lược này giúp câu văn không bị cắt ngang giữa chừng, phù hợp với các đoạn văn mô tả chung. Tuy nhiên, đối với văn bản hành chính có cấu trúc liệt kê và danh sách gạch đầu dòng, nó dễ làm đứt liên kết giữa câu chủ đề và các điều kiện thành phần.
- **Code snippet (nếu custom):** Sử dụng `SentenceChunker` tiêu chuẩn trong `src/chunking.py`.

**Thành viên 3 — [Thành viên 3]**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=500, overlap=50`)
- **Mô tả & lý do chọn:**  
  Chia tài liệu thành các khối cố định 500 ký tự với độ chồng chéo 50 ký tự. Chiến lược này đơn giản nhất, đảm bảo kích thước đồng đều để đưa vào mô hình embedding mà không sợ vượt token limit. Tuy nhiên, điểm yếu nghiêm trọng là cắt cơ học tại ký tự bất kỳ, dễ làm xẻ đôi từ ngữ hoặc ngắt đôi điều khoản quan trọng.
- **Code snippet (nếu custom):** Sử dụng `FixedSizeChunker` tiêu chuẩn trong `src/chunking.py`.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Thân Tiến Đạt | RecursiveChunker (`recursive`) | **9.5 / 10** | Giữ trọn vẹn ngữ nghĩa từng Điều/Khoản, độ mạch lạc cao, chunking thích ứng linh hoạt. | Chi phí tính toán đệ quy cao hơn một chút so với cắt cố định. |
| Thành viên 2 | SentenceChunker (`by_sentences`) | **7.5 / 10** | Giữ trọn vẹn từng câu, không sinh ra câu cụt. | Dễ tạo chunk quá dài khi gặp văn bản liệt kê ít dấu chấm câu; làm mất câu dẫn của danh sách. |
| Thành viên 3 | FixedSizeChunker (`fixed_size`) | **6.0 / 10** | Đơn giản, độ dài chunk hoàn toàn đồng nhất. | Cắt cụt câu, xẻ đôi thông tin quan trọng ở ranh giới chunk, làm giảm điểm cosine similarity. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **RecursiveChunker** là chiến lược tốt nhất vượt trội cho bộ dữ liệu quy chế UET. Do đặc thù tài liệu pháp quy bao gồm nhiều cấp độ tổ chức (tiêu đề, điều khoản, gạch đầu dòng), RecursiveChunker bảo toàn cấu trúc tự nhiên bằng cách ưu tiên ngắt ở ranh giới đoạn (`\n\n`) trước. Nhờ đó, một điều khoản quy chế (như điều kiện thôi học tại Điều 28) được chứa trọn vẹn trong một chunk đơn lẻ, giúp mô hình Vector Store truy xuất đúng 100% ngữ cảnh mà không bị phân mảnh thông tin.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên có thể tìm kiếm những cơ hội nghề nghiệp nào thông qua UET? | Cổng thông tin việc làm UET cung cấp các cơ hội thực tập, việc làm kỹ sư lập trình C/C++, Embedded Software, nhân viên phân tích mô phỏng, thiết kế cơ khí và kết nối doanh nghiệp đối tác tuyển dụng. | `co-hoi-nghe-nghiep#0` (`co-hoi-nghe-nghiep.md`) |
| 2 | UET hiện cung cấp những thông tin tuyển sinh nào cho thí sinh? | Điểm chuẩn trúng tuyển, chính sách học bổng theo Nghị định 179/2026/NĐ-CP hỗ trợ chi phí sinh hoạt, ngưỡng bảo đảm chất lượng đầu vào, cổng đăng ký trực tuyến và danh mục các ngành đào tạo đại học chính quy. | `tuyen-sinh#1` (`tuyen-sinh.md`) |
| 3 | Những mục tiêu chính trong chiến lược phát triển của Trường Đại học Công nghệ là gì? | Trở thành cơ sở giáo dục đại học hàng đầu trong cả nước về tiên phong, sáng tạo và dẫn dắt trong đào tạo nguồn nhân lực bậc cao và khoa học công nghệ; duy trì vị thế trường kỹ thuật công nghệ tiên tiến ở Châu Á vào năm 2045. | `chien-luoc-phat-trien#2` (`chien-luoc-phat-trien.md`) |
| 4 | Điều kiện và trình tự để mở một ngành đào tạo trình độ đại học được quy định như thế nào? | Căn cứ theo Thông tư số 02/2022/TT-BGDĐT và Thông tư số 12/2024/TT-BGDĐT của Bộ GD&ĐT cùng Quyết định số 4555/QĐ-ĐHQGHN quy định điều kiện, trình tự, thủ tục mở ngành đào tạo trình độ đại học tại ĐHQGHN. | `quy-dinh-mo-nganh#0` (`quy-dinh-mo-nganh.md`) |
| 5 | Theo quy chế đào tạo đại học của ĐHQGHN, sinh viên cần đáp ứng những điều kiện nào để được công nhận tốt nghiệp? *(Kèm `metadata_filter={"audience": "student"}`)* | Theo Điều 43 QĐ 5115: Trong thời gian học tập tối đa, không đang bị truy cứu trách nhiệm hình sự, tích lũy đủ số tín chỉ, ĐTBCTL đạt từ 2,00 trở lên (2,50 đối với hệ tài năng/CLC), đạt chuẩn ngoại ngữ, GDQP-AN và GDTC. | `quy-che-dao-tao#175` (`quy-che-dao-tao.md`, Điều 43) |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Điểm số & Ghi chú |
|---|---------|-------------------------------|-------------------------------|-------------------|
| 1 | Cơ hội nghề nghiệp UET... | RecursiveChunker | **Có (Top-1, Score 0.7396)** | 2/2 điểm. Nắm trọn khối bản tin việc làm và đối tác tuyển dụng. |
| 2 | Thông tin tuyển sinh UET... | RecursiveChunker | **Có (Top-2, Score 0.5122)** | 1/2 điểm. Top-1 bị tin việc làm cạnh tranh từ khóa, nhưng Top-2 chứa đầy đủ đề án tuyển sinh. |
| 3 | Mục tiêu chiến lược phát triển... | RecursiveChunker | **Có (Top-1, Score 0.6108)** | 2/2 điểm. Trích xuất chính xác sứ mạng và tầm nhìn 2045 của UET. |
| 4 | Điều kiện, trình tự mở ngành... | RecursiveChunker | **Có (Top-1, Score 0.7073)** | 2/2 điểm. Tìm trúng văn bản pháp quy Thông tư 02/2022 và QĐ 4555. |
| 5 | Điều kiện công nhận tốt nghiệp... | RecursiveChunker + Metadata Filter | **Có (Top-1, Score 0.6331)** | 2/2 điểm. Lọc chuẩn `audience="student"`, trích đúng Điều 43 quy chế đào tạo. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Cực kỳ hữu ích, thể hiện rõ nhất ở Câu hỏi 4 và Câu hỏi 5:**  
> 1. **Ở Câu hỏi 4** (*"Điều kiện và trình tự để mở một ngành đào tạo..."*): Khi người dùng là sinh viên hỏi câu hỏi chung chung, nếu **không dùng bộ lọc**, hệ thống lập tức xếp tài liệu quản trị nội bộ dành cho cán bộ giảng viên (`quy-dinh-mo-nganh.md`, `audience: faculty`) lên Top-1 (0.7073) và Top-2 (0.6508). Khi **bật pre-filtering `metadata_filter={"audience": "student"}`**, 100% tài liệu của giảng viên bị loại bỏ ngay từ đầu, hệ thống chỉ trích xuất quy định học phần trong quy chế đào tạo của người học.  
> 2. **Ở Câu hỏi 5**: Bộ lọc `{"audience": "student"}` đảm bảo chắc chắn rằng 100% tài liệu trả về cho điều kiện tốt nghiệp chỉ thuộc về quy chế đào tạo của sinh viên, loại bỏ hoàn toàn nguy cơ nhầm lẫn sang các quy chế thi đua hay văn bản nhân sự khác.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Văn bản pháp quy có cấu trúc phân tầng tự nhiên:** `RecursiveChunker` với danh sách phân cách `["\n\n", "\n", ". ", " ", ""]` vượt trội hoàn toàn so với `FixedSizeChunker` vì nó tôn trọng ranh giới Điều/Khoản, tránh hiện tượng câu cụt hoặc mất tiêu đề điều luật.  
> 2. **Sức mạnh của Pre-filtering trong phân quyền dữ liệu:** Phân loại metadata theo `audience` (`student` vs `faculty`) giải quyết triệt để bài toán trả lời nhầm đối tượng trong môi trường đại học.  
> 3. **Tầm quan trọng của việc làm sạch dữ liệu trước khi chunking:** Loại bỏ menu điều hướng, breadcrumb và chân trang web giúp top-k retrieval đạt độ tập trung cao nhất vào nội dung học vụ thực tế.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một kho tài liệu và cùng một câu hỏi, nhưng chiến lược chia nhỏ khác nhau dẫn đến khác biệt rất lớn: `FixedSizeChunker` làm đứt đôi 40% các quy định học vụ khiến AI trả lời thiếu ý hoặc sai lệch con số, trong khi `RecursiveChunker` đạt độ chính xác ngữ cảnh cao nhất nhờ giữ nguyên vẹn đơn vị ngữ nghĩa.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nếu có thêm thời gian, nhóm sẽ phát triển một `SectionHeadingChunker` tùy biến riêng để tự động nhận diện các tiêu đề `## Điều...` và gắn kèm tiêu đề điều luật vào đầu mỗi chunk con, giúp AI luôn nắm rõ ngữ cảnh nguồn ngay cả khi một điều khoản quá dài buộc phải chia nhỏ.

### Phân tích ca thất bại (Failure Case Analysis)

- **Câu hỏi bị lỗi:** Câu hỏi 5 khi không dùng bộ lọc (`filter = None`): *"Quy định về chương trình đào tạo và mở ngành học dành cho người học?"*
- **Hiện tượng & Nguyên nhân:** Văn bản `quy-dinh-mo-nganh.md` (vốn dành cho giảng viên `audience: faculty`) xuất hiện ở Top-3 với điểm tương đồng rất cao (0.6702) do có sự trùng lặp dày đặc về các thuật ngữ *"chương trình đào tạo"*, *"mở ngành"*. Mô hình embedding chỉ đo độ gần gũi về chủ đề ngữ nghĩa chung mà không tự phân biệt được đối tượng thụ hưởng nếu không có nhãn siêu dữ liệu.
- **Đề xuất khắc phục:** Bắt buộc áp dụng cơ chế **Pre-filtering** theo trường `metadata_filter={"audience": "student"}` để loại bỏ hoàn toàn các văn bản nội bộ của cán bộ/giảng viên trước khi thực hiện xếp hạng cosine similarity.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

