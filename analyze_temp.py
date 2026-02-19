
import pdfplumber

def analyze_pdf(path):
    try:
        with pdfplumber.open(path) as pdf:
            print(f"Total Pages: {len(pdf.pages)}")
            if len(pdf.pages) > 0:
                text = pdf.pages[0].extract_text()
                print("--- PAGE 1 TEXT START ---")
                print(text)
                print("--- PAGE 1 TEXT END ---")
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    analyze_pdf("input.pdf")
