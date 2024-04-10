# main code
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import tempfile
import os
from streamlit_pdf_viewer import pdf_viewer
import shutil
import PyPDF2

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

def main():
    st.title("PDF Viewer Web App")
    st.write("Upload a PDF file to view it below:")
    
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    pdf_file = st.file_uploader("Upload PDF file", type=('pdf'), key='pdf')
    if pdf_file:
        file_path = os.path.join("uploads", pdf_file.name)
        with open(file_path, "wb") as f:
            f.write(pdf_file.getvalue())

        check_encrypted(file_path)

        st.session_state.pdf_ref = pdf_file  # Backup the uploaded PDF reference

    if st.session_state.pdf_ref:
        binary_data = st.session_state.pdf_ref.getvalue()
        pdf_stream = BytesIO(binary_data)
        pdf_reader = PdfReader(pdf_stream)

        num_pages = len(pdf_reader.pages)

        for page_num in range(num_pages):
            st.subheader(f"Page {page_num + 1}")
            page = pdf_reader.pages[page_num]
            pdf_writer = PdfWriter()
            pdf_writer.add_page(page)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                pdf_writer.write(temp_file)
                temp_file_path = temp_file.name

            pdf_viewer(temp_file_path, width=700)
            os.unlink(temp_file_path)

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
