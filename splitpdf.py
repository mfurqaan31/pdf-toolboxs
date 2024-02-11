# main code
import PyPDF2
import streamlit as st
from io import BytesIO
import os
import atexit
import shutil
import zipfile

def check_encrypted(pdf_file_path):
    is_encrypted = False
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        is_encrypted = pdf_reader.is_encrypted

    if is_encrypted:
        st.error("The selected PDF is encrypted. Cannot convert to images.")
        st.stop()

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)

def split_pdf(pdf_path, page_ranges):
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)

    split_pdfs = []
    for start, end in page_ranges:
        start = max(1, start)
        end = min(total_pages, end)

        pdf_writer = PyPDF2.PdfWriter()
        for page_num in range(start - 1, end):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        split_pdf_bytes = BytesIO()
        pdf_writer.write(split_pdf_bytes)
        split_pdfs.append(split_pdf_bytes)

    pdf_file.close()
    return split_pdfs

def merge_pdfs(split_pdfs):
    merged_pdf_writer = PyPDF2.PdfWriter()
    for pdf_bytes in split_pdfs:
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        for page_num in range(len(pdf_reader.pages)):
            merged_pdf_writer.add_page(pdf_reader.pages[page_num])

    merged_pdf_bytes = BytesIO()
    merged_pdf_writer.write(merged_pdf_bytes)
    return merged_pdf_bytes

def main():
    st.title("PDF Page Splitter")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        pdf_path = os.path.join("uploads", uploaded_file.name)

        os.makedirs("uploads", exist_ok=True)
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(uploaded_file.getvalue())

        check_encrypted(pdf_path)

        pdf_reader = PyPDF2.PdfReader(pdf_path)
        total_pages = len(pdf_reader.pages)

        page_ranges = st.text_input("Enter page ranges (e.g., 1-3, 4-6):")
        zip_filename = st.text_input("Enter the name for the output file without any extension:","output")
        zip_filename = zip_filename.split('.')[0]
        merge_checkbox = st.checkbox("Merge all ranges to form a single PDF")

        if page_ranges.strip() and zip_filename.strip():
            try:
                ranges = [list(map(int, rng.split('-'))) for rng in page_ranges.split(',')]
                if all(1 <= start <= end <= total_pages for start, end in ranges):
                    if st.button("Split PDF"):
                        split_pdfs = split_pdf(pdf_path, ranges)

                        if merge_checkbox:
                            merged_pdf_bytes = merge_pdfs(split_pdfs)
                            st.success(f"The PDFs have been merged, and the PDF is ready for Download.")
                            st.download_button(label=f"Download {zip_filename}.pdf", data=merged_pdf_bytes.getvalue(), file_name=f"{zip_filename}.pdf")
                        else:
                            zip_filename_with_extension = os.path.join("uploads", f"{zip_filename}.zip")
                            with zipfile.ZipFile(zip_filename_with_extension, 'w') as zip_file:
                                for i, pdf_bytes in enumerate(split_pdfs):
                                    pdf_filename = f"split_pdf_{i + 1}.pdf"
                                    zip_file.writestr(pdf_filename, pdf_bytes.getvalue())

                            st.success(f"The PDFs have been split, and the ZIP file is ready for Download.")
                            st.download_button(label=f"Download {zip_filename}.zip", data=open(zip_filename_with_extension, 'rb').read(), file_name=f"{zip_filename}.zip")

                else:
                    st.warning("Invalid page range. Make sure all ranges are in the correct format and within the total number of pages.")

            except ValueError:
                st.warning("Invalid page range format. Please use the format 'start-end, start-end'")
        else:
            st.warning("Please enter page ranges and a zip file name before splitting.")

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
