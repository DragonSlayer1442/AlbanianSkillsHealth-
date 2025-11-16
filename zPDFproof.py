import fitz # PyMuPDF

def extract_text_from_pdf_pymupdf(pdf_path):
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"Error extracting text with PyMuPDF: {e}")
        return text

    # Example usage:
pdf_file = "reports/medical-report.pdf" # Replace with your PDF file path
extracted_text = extract_text_from_pdf_pymupdf(pdf_file)
print(extracted_text)