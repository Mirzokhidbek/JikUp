from fpdf import FPDF


def make_pdf(lines: list[str], pages: int = 1) -> bytes:
    pdf = FPDF()
    pdf.set_font("Helvetica", size=11)
    for _ in range(pages):
        pdf.add_page()
        for line in lines:
            pdf.multi_cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())


RESUME_LINES = [
    "Aziz Karimov - Backend Developer",
    "Email: aziz@example.com",
    "Skills: Python, FastAPI, PostgreSQL, Docker, AWS",
    "Experience: Backend developer at Example LLC, 2023-2025 (2 years)",
    "Project: Delivery tracking API built with FastAPI and Redis, reduced latency by 40%",
    "Languages: Korean TOPIK 4, English IELTS 6.5",
]
