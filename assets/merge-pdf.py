# main code
import streamlit as st
from streamlit_sortables import sort_items
import fitz
import io
import os
import shutil
import atexit

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)

def is_encrypted(pdf_bytes):
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        encrypted = pdf_document.is_encrypted
        pdf_document.close()
        return encrypted
    except Exception as e:
        st.error(f"Error checking encryption status: {e}")
        return True

def merge_pdf(uploaded_paths, file_names, reordered_names, output_pdf_name):
    pdf_writer = fitz.open()

    for name in reordered_names:
        index = file_names.index(name)
        pdf_path = uploaded_paths[index]
        pdf_bytes = open(pdf_path, "rb").read()

        if is_encrypted(pdf_bytes):
            pdf_path = pdf_path.split("/")[-1]
            st.warning(f"{pdf_path}" + " is encrypted, hence will not be considered for merging please remove it")
            st.stop()

        try:
            pdf_writer.insert_pdf(fitz.open(stream=pdf_bytes, filetype="pdf"), from_page=0, to_page=-1)
        except ValueError as e:
            st.error(f"Error adding {pdf_path} to the merged PDF: {e}")

    merged_pdf_io = io.BytesIO()
    pdf_writer.save(merged_pdf_io)
    pdf_writer.close()

    st.success("The PDFs have been merged, and it is ready for download.")
    st.download_button(
        label="Download PDF",
        data=merged_pdf_io.getvalue(),
        file_name=output_pdf_name,
        key="merged_pdf_button"
    )

def save_uploaded_files(uploaded_files):
    uploaded_paths = []

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    filename_occurrences = {}

    for uploaded_file in uploaded_files:
        base_filename, file_extension = os.path.splitext(uploaded_file.name)

        if base_filename not in filename_occurrences:
            filename_occurrences[base_filename] = 0
            new_filename = base_filename
        else:
            filename_occurrences[base_filename] += 1
            new_filename = f"{base_filename}({filename_occurrences[base_filename]})"

        file_path = os.path.join("uploads", new_filename + file_extension)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        uploaded_paths.append(file_path)
    return uploaded_paths

def main():
    st.title("Merge PDFs")

    uploaded_files = st.file_uploader("Add PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        uploaded_paths = save_uploaded_files(uploaded_files)
        file_names = [os.path.basename(path) for path in uploaded_paths]
        st.write("Arrange the order of the pdf")
        reordered_names = sort_items(file_names)
        st.write("Order for the uploaded PDF files:")

        for index, name in enumerate(reordered_names):
            st.write(f"{index + 1}. {name}")

        output_pdf_name = st.text_input("Enter the name of the output PDF file (without extension):", "merged_pdf")
        output_pdf_name=output_pdf_name.split('.')[0]

        if st.button("Merge Pdfs"):
            merge_pdf(uploaded_paths, file_names, reordered_names, f"{output_pdf_name}.pdf")

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
