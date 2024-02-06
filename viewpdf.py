# has slider
import streamlit as st
import io
from PIL import Image
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF

def display_pdf_page(pdf_bytes, page_number):
    pdf_document = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
    if page_number <= 0 or page_number > pdf_document.page_count:
        st.write(f"Invalid page number. Please enter a page number between 1 and {pdf_document.page_count}.")
    else:
        # Convert the PDF page to an image
        images = convert_from_bytes(pdf_bytes, first_page=page_number, last_page=page_number)
        if images:
            # Display the image
            st.image(images[0], caption=f"Page {page_number}", use_column_width=True)
        else:
            st.write("Error converting PDF to image.")

def main():
    st.title("Edit PDF")
    # Upload PDF file
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        page_number = st.slider("Select page number", 1, fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf").page_count, 1)
        display_pdf_page(pdf_bytes, page_number)

    else:
        st.write("Please upload a PDF file.")

if __name__ == "__main__":
    main()
