import re
import pdfplumber
from datetime import date
from schema import Invoice, Seller, Customer, InvoiceMeta, InvoiceItem, InvoiceTotals, BankDetails

def extract_pdf_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def parse_with_regex(text):
    # --- strategies ---
    # 1. Bank Details
    bank_name = re.search(r"Bank Name\s*[:\-]\s*(.*)", text, re.IGNORECASE)
    ac_name = re.search(r"Account Name\s*[:\-]\s*(.*)", text, re.IGNORECASE)
    ifsc = re.search(r"IFSC Code\s*[:\-]\s*([A-Z0-9]+)", text, re.IGNORECASE)
    ac_no = re.search(r"Account No\s*[:\-]\s*(\d+)", text, re.IGNORECASE)
    upi = re.search(r"Bank UPI\s*[:\-]\s*(\S+)", text, re.IGNORECASE)

    bank_details = BankDetails(
        bank_name=bank_name.group(1).strip() if bank_name else "Unknown Bank",
        account_name=ac_name.group(1).strip() if ac_name else None,
        ifsc=ifsc.group(1).strip() if ifsc else None,
        account_no=ac_no.group(1).strip() if ac_no else None,
        upi=upi.group(1).strip() if upi else None
    )

    # 2. Seller (Heuristic: First few lines often contain seller name)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    seller_name = lines[1] if len(lines) > 1 else "Unknown Seller" # Assuming 'TAX INVOICE' is line 0
    seller_address = lines[2] if len(lines) > 2 else "Unknown Address"
    
    # Try to find email/phone
    email = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", text)
    mobile = re.search(r"(\+?\d[\d -]{8,12}\d)", text)

    seller = Seller(
        name=seller_name,
        address=seller_address,
        email=email.group(1) if email else None,
        mobile=mobile.group(1) if mobile else None
    )

    # 3. Totals
    # Look for "Grand Total" or "Total" followed by number
    total_match = re.search(r"(?:Grand Total|Invoice Total)\s*[:\-]?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
    invoice_total = 0.0
    if total_match:
        try:
            invoice_total = float(total_match.group(1).replace(',', ''))
        except:
            pass
            
    # Fallback to verify text dump if specific fields fail
    
    # 4. Meta
    invoice_no_match = re.search(r"Invoice No\.?\s*[:\-]?\s*([A-Za-z0-9/-]+)", text, re.IGNORECASE)
    date_match = re.search(r"Date\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.IGNORECASE)
    
    # Default date if not found
    inv_date = date.today()
    # Simple date parser could be added here if needed, but for now defaulting is safer than crashing
    
    meta = InvoiceMeta(
        invoice_number=invoice_no_match.group(1) if invoice_no_match else "INV-001",
        invoice_date=inv_date
    )

    # 5. Customer (Very hard to distinguish from Seller without specific layout keywords "Bill To", etc in unstructured text)
    # We will use placeholders for now as requested "Simple version"
    customer = Customer(
        name="Cash/General",
        address="N/A"
    )

    # 6. Items - extremely hard with pure Regex on unstructured text without OCR layout preservation
    # Check for "Total"
    
    totals = InvoiceTotals(
        taxable_total=invoice_total, # Simplified assumption
        invoice_total=invoice_total
    )

    return Invoice(
        seller=seller,
        customer=customer,
        invoice_meta=meta,
        items=[], # Empty items list for simple version
        totals=totals,
        bank_details=bank_details
    )

def extract_invoice_structured(text):
    return parse_with_regex(text)
