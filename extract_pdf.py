import sys
try:
    import fitz
    doc = fitz.open(sys.argv[1])
    text = ""
    for page in doc:
        text += page.get_text()
    print("--- PYMUPDF SUCCESS ---")
    print(text[:6000])
except Exception as e1:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(sys.argv[1])
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        print("--- PYPDF2 SUCCESS ---")
        print(text[:6000])
    except Exception as e2:
        print(f"Failed both. e1: {e1}, e2: {e2}")
