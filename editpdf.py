import streamlit as st
import io
from PIL import Image
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF

def display_pdf_page(uploaded_file, page_number):
    pdf_document = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
    if page_number <= 0 or page_number > pdf_document.page_count:
        st.write(f"Invalid page number. Please enter a page number between 1 and {pdf_document.page_count}.")
    else:
        # Convert the PDF page to an image
        pdf_bytes = uploaded_file.read()
        images = convert_from_bytes(pdf_bytes, first_page=page_number, last_page=page_number)
        if images:
            # Display the image
            st.image(images[0], caption=f"Page {page_number}", use_column_width=True)
        else:
            st.write("Error converting PDF to image.")

# Upload PDF file
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

# Choose the page to display
page_number = st.number_input("Enter page number", min_value=1, value=1)

if uploaded_file is not None:
    display_pdf_page(uploaded_file, page_number)
else:
    st.write("Please upload a PDF file.")
