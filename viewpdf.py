# main code
import os
import streamlit as st
from pdf2image import convert_from_bytes
import fitz
import PyPDF2
import atexit
import shutil

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)

def check_encrypted(pdf_file_path):
    is_encrypted = False
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        is_encrypted = pdf_reader.is_encrypted

    if is_encrypted:
        st.error("The selected PDF is encrypted.")
        st.stop()

def display_pdf_page(uploaded_file, page_number):
    pdf_document = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
    if page_number <= 0 or page_number > pdf_document.page_count:
        st.write(f"Invalid page number. Please enter a page number between 1 and {pdf_document.page_count}.")
    else:
        pdf_bytes = uploaded_file.read()
        images = convert_from_bytes(pdf_bytes, first_page=page_number, last_page=page_number)
        if images:
            st.image(images[0], caption=f"Page {page_number}", use_column_width=True)
        else:
            st.write("Error converting PDF to image.")

def main():
    st.title("View your PDF")
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file is not None:
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        check_encrypted(file_path)

        page_number = st.number_input("Enter page number", min_value=1, value=1)
        display_pdf_page(uploaded_file, page_number)
    else:
        st.write("Please upload a PDF file.")

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
