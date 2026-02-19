import streamlit as st
from extractor import extract_pdf_text, extract_invoice_structured
from renderer import render_invoice

st.title("Invoice Format Converter")

uploaded_file = st.file_uploader("Upload Input Invoice", type="pdf")

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    text = extract_pdf_text("temp.pdf")
    if not text.strip():
        st.error("Could not extract text. If this is a scanned PDF, this free version cannot process it.")
    else:
        structured_data = extract_invoice_structured(text)

        render_invoice(structured_data, "output_invoice.pdf")

        st.success("Invoice Converted Successfully!")
        st.download_button("Download Invoice", open("output_invoice.pdf", "rb"))
