# main code
import os
import streamlit as st
import PyPDF2
import atexit
import shutil
import base64

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

def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

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
        
        displayPDF(file_path)
    else:
        st.write("Please upload a PDF file.")

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
