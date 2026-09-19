import csv
import re
from pathlib import Path

D = Path("data/university")  # Đổi lại nếu dùng thư mục khác
REQ = ["doc_id", "title", "source_url", "retrieved_at", "document_version", "audience"]

mds = sorted(D.glob("*.md"))
rows = list(csv.DictReader(open(D / "sources.csv", encoding="utf-8")))

ids, auds = [], {}

for p in mds:
    frontmatter = p.read_text(encoding="utf-8").split("---", 2)[1]
    fm = {}
    for k, v in re.findall(r"^(\w+):\s*(.+)$", frontmatter, re.M):
        # Loại bỏ comment sau dấu # và dấu ngoặc kép / khoảng trắng
        clean_v = re.sub(r"\s*#.*$", "", v).strip("\"' ")
        fm[k] = clean_v

    ids.append(fm.get("doc_id"))
    auds[fm.get("audience")] = auds.get(fm.get("audience"), 0) + 1

    status = "OK" if all(k in fm for k in REQ) and fm.get("doc_id") == p.stem else "THIEU METADATA"
    print(f"{p.name:40} {status}")

print("so file :", len(mds), "(can 5-10)")
print("csv     :", "khop" if sorted(r["doc_id"] for r in rows) == sorted(ids) else "LECH")
print("audience:", auds)