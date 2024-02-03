# downloads zip file
import os
import atexit
import shutil
import streamlit as st
import PyPDF2
import zipfile
from io import BytesIO

def cleanup():
    # Delete 'uploads' folder when the application exits
    shutil.rmtree("uploads", ignore_errors=True)

def split_pdf(pdf_path, page_ranges):
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)

    split_pdfs = []
    for start, end in page_ranges:
        if 1 <= start <= end <= total_pages:
            pdf_writer = PyPDF2.PdfWriter()  # Use PdfWriter instead of PdfFileWriter
            for page_num in range(start - 1, end):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            split_pdf_bytes = BytesIO()
            pdf_writer.write(split_pdf_bytes)
            split_pdfs.append(split_pdf_bytes)

    pdf_file.close()
    return split_pdfs

def main():
    st.title("PDF Page Splitter")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Save the uploaded file to the 'uploads' folder
        pdf_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(uploaded_file.getvalue())

        page_ranges = st.text_input("Enter page ranges (e.g., 1-3, 4-6):")

        if page_ranges.strip():  # Check if the input is not empty
            try:
                ranges = [list(map(int, rng.split('-'))) for rng in page_ranges.split(',')]

                if st.button("Split PDF"):
                    split_pdfs = split_pdf(pdf_path, ranges)
                    
                    # Create a zip file to store all split PDFs
                    zip_filename = "split_pdfs.zip"
                    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                        for i, pdf_bytes in enumerate(split_pdfs):
                            pdf_filename = f"split_pdf_{i + 1}.pdf"
                            zip_file.writestr(pdf_filename, pdf_bytes.getvalue())

                    # Provide a single download button for the zip file
                    st.markdown(f"**Download Split PDFs**")
                    st.download_button(label="Download Zip File", data=open(zip_filename, 'rb').read(), file_name=zip_filename)

            except ValueError:
                st.error("Invalid page range format. Please use the format 'start-end, start-end'")
        else:
            st.warning("Please enter page ranges before splitting.")

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
