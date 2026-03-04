# 로컬 실행용: PDF에서 특정 페이지 범위 텍스트 추출
# pip install pymupdf
import fitz

pdf_path = "junos_cli-reference.pdf"
out_path = "junos_cli.txt"

start_page = 2220 - 1  # 0-based
end_page = 32857 - 1

doc = fitz.open(pdf_path)
with open(out_path, "w", encoding="utf-8") as f:
    for i in range(start_page, end_page + 1):
        text = doc.load_page(i).get_text("text")
        f.write(text)
        f.write("\n\n")

print("done:", out_path)
