# main code
import streamlit as st
import fitz
from PIL import Image
import zipfile
from io import BytesIO
import PyPDF2
import os
import shutil
import atexit

def check_encrypted(pdf_file_path):
    is_encrypted = False
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        is_encrypted = pdf_reader.is_encrypted

    if is_encrypted:
        st.error("The selected PDF is encrypted. Cannot convert to images.")
        st.stop()

def convert_pdf_to_zip(pdf_file_path, dpi=300):
    pdf_document = fitz.open(pdf_file_path)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            pix = page.get_pixmap(dpi=dpi)

            pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            image_filename = f"page_{page_number + 1}.png"
            with BytesIO() as image_bytes:
                pil_image.save(image_bytes, format="PNG", quality=95)
                image_data = image_bytes.getvalue()
                zip_file.writestr(image_filename, image_data)

    return zip_buffer.getvalue()

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)

def main():
    st.title("PDF to Image Converter")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        pdf_file_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)

        with open(pdf_file_path, 'wb') as pdf_file:
            pdf_file.write(uploaded_file.read())

        check_encrypted(pdf_file_path)

        zip_filename = st.text_input("Enter the ZIP file name (without extension):", "output", key="zip_filename")

        if uploaded_file and zip_filename:
            zip_filename = zip_filename.strip()
            zip_filename = zip_filename.split('.')[0]

            if not zip_filename.endswith(".zip"):
                zip_filename += ".zip"

            if st.button("Convert to ZIP"):
                st.success(f"The PDF has been converted to images, and the ZIP file is ready for Download.")
                zip_data = convert_pdf_to_zip(pdf_file_path, dpi=300)
                st.download_button(
                    label="Download ZIP",
                    data=zip_data,
                    file_name=zip_filename,
                    key="download_zip_button"
                )

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
