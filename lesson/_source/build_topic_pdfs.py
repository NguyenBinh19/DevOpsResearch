"""Build one PDF per DevOps topic, without stage folders."""

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer

from pdf_layout import BLUE, GRAY, ROOT, STYLES, code_block, parse_markdown, safe


SOURCE = ROOT / "lesson" / "topics" / "_source"
OUTPUT = ROOT / "lesson" / "topics"
APPENDICES = {
    "05-python-api": [ROOT / "lesson/labs/notes-api/app.py"],
    "06-docker": [ROOT / "lesson/labs/notes-api/Dockerfile", ROOT / "lesson/labs/notes-api/compose.yaml"],
    "08-terraform": [ROOT / "lesson/labs/terraform-local/main.tf"],
    "10-kubernetes": [ROOT / "lesson/labs/kubernetes-local/web.yaml"],
    "12-argocd": [ROOT / "lesson/labs/argocd-local/guestbook-lab.yaml"],
    "11-helm": list(sorted((ROOT / "lesson/labs/helm-notes").rglob("*.yaml"))),
    "22-edge": [ROOT / "lesson/labs/edge-local/compose.yaml", ROOT / "lesson/labs/edge-local/nginx.conf"],
}


def footer(canvas, doc):
    canvas.saveState()
    w, _ = A4
    canvas.setStrokeColor(colors.HexColor("#CDDCE8"))
    canvas.line(21 * mm, 17 * mm, w - 21 * mm, 17 * mm)
    canvas.setFont("Arial", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(21 * mm, 12.5 * mm, "DevOps Research | Chuyên đề độc lập")
    canvas.drawRightString(w - 21 * mm, 12.5 * mm, f"Trang {doc.page}")
    canvas.restoreState()


def build_one(source: Path):
    slug = source.stem
    title = source.read_text(encoding="utf-8").splitlines()[0].removeprefix("# ")
    target = OUTPUT / f"{slug}.pdf"
    doc = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=21 * mm, rightMargin=21 * mm,
                            topMargin=23 * mm, bottomMargin=22 * mm, title=title,
                            author="DevOps Research", subject="Bài giảng DevOps theo chủ đề")
    story = [Spacer(1, 27 * mm), Paragraph(safe(title), STYLES["cover"]),
             HRFlowable(width="100%", thickness=2, color=BLUE), Spacer(1, 7 * mm),
             Paragraph("Một chủ đề, một tài liệu: mô hình, bài tập, lỗi thường gặp và câu hỏi phỏng vấn.", STYLES["subcover"]),
             Spacer(1, 15 * mm), Paragraph("Đọc theo thứ tự trong tập. Làm lab trên môi trường riêng, ghi kết quả và đối chiếu tài liệu chính thức theo phiên bản bạn đang dùng.", STYLES["body"]),
             Paragraph("Bám theo bốn JD người học cung cấp | 11/10/2026", STYLES["small"]), PageBreak()]
    story.extend(parse_markdown(source.read_text(encoding="utf-8")))
    if slug in APPENDICES:
        story.append(Spacer(1, 9 * mm))
        story.append(Paragraph("Phụ lục: mã lab để đọc offline", STYLES["h2"]))
        for file in APPENDICES[slug]:
            story.append(Paragraph(safe(file.relative_to(ROOT).as_posix()), STYLES["h3"]))
            story.extend(code_block(file.read_text(encoding="utf-8").splitlines()))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return target


if __name__ == "__main__":
    requested = set(sys.argv[1:])
    for source in sorted(SOURCE.glob("[0-9][0-9]-*.md")):
        if requested and source.stem not in requested:
            continue
        print(build_one(source))
