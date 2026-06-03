import pypdf, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

reader = pypdf.PdfReader("Copy of Python Developer Intern Assignemment .pdf")
for i, page in enumerate(reader.pages):
    print(f"--- PAGE {i+1} ---")
    print(page.extract_text())
    print()
