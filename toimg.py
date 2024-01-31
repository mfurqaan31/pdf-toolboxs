# getting stored in downloads
import streamlit as st
import fitz
from PIL import Image
import zipfile
from io import BytesIO
import PyPDF2
import os

def check_encrypted(pdf_file_path):
    is_encrypted = False
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        is_encrypted = pdf_reader.is_encrypted

    if is_encrypted:
        st.error("The selected PDF is encrypted. Cannot convert to images.")
        st.stop()

def convert_pdf_to_zip(pdf_file_path):
    pdf_document = fitz.open(pdf_file_path)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            image_list = page.get_pixmap()

            pil_image = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)

            image_filename = f"page_{page_number + 1}.png"
            with BytesIO() as image_bytes:
                pil_image.save(image_bytes, format="PNG")
                image_data = image_bytes.getvalue()
                zip_file.writestr(image_filename, image_data)

    # Return the bytes of the generated ZIP file
    return zip_buffer.getvalue()

def main():
    st.title("PDF to Image Converter")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        pdf_file_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)

        with open(pdf_file_path, 'wb') as pdf_file:
            pdf_file.write(uploaded_file.read())

        check_encrypted(pdf_file_path)

        zip_filename = st.text_input("Enter the ZIP file name with extension:", "output.zip", key="zip_filename")
        
        # Check if the user has selected a PDF and entered a ZIP file name
        if uploaded_file and zip_filename:
            # Trigger the conversion when the button is clicked
            if st.button("Convert to ZIP"):
                zip_data = convert_pdf_to_zip(pdf_file_path)
                st.download_button(
                    label="Download ZIP",
                    data=zip_data,
                    file_name=zip_filename,
                    key="download_zip_button"
                )
                st.success(f"The PDF converted to images, and the ZIP file is ready for download.")

if __name__ == "__main__":
    main()
