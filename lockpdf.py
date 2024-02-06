import streamlit as st
import PyPDF2
import os
import shutil
import atexit
import io

def check_encrypted(pdf_file_path):
    is_encrypted = False
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        is_encrypted = pdf_reader.is_encrypted

    if is_encrypted:
        st.error("The selected PDF is encrypted.")
        st.stop()

def remove_uploads_folder():
    # Remove the "uploads" folder when the program exits
    shutil.rmtree("uploads", ignore_errors=True)

def encryption(password, file_path, output_name):
    # Create a PdfWriter to write the encrypted PDF
    pdf_writer = PyPDF2.PdfWriter()

    # Open the input PDF file and add pages to the writer
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    # Encrypt the PDF with the provided password
    pdf_writer.encrypt(user_password=password, owner_pwd=None, use_128bit=True)

    # Write the encrypted PDF to a BytesIO buffer
    encrypt_pdf_io = io.BytesIO()
    pdf_writer.write(encrypt_pdf_io)

    # Seek to the beginning of the BytesIO buffer
    encrypt_pdf_io.seek(0)

    # Success message and download button
    st.success("The PDF has been encrypted and is ready for download.")
    st.download_button(
        label="Download PDF",
        data=encrypt_pdf_io.getvalue(),
        file_name=output_name,
        mime="application/pdf",
        key="encrypt_pdf_button"
    )

def main():
    st.title("PDF Encrypter")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        pdf_file_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)

        with open(pdf_file_path, 'wb') as pdf_file:
            pdf_file.write(uploaded_file.read())

        check_encrypted(pdf_file_path)

        output_name = st.text_input("Enter the ZIP file name (without extension):", "output", key="output_name")

        # Check if the user has selected a PDF and entered a ZIP file name
        if uploaded_file and output_name:
            output_name = output_name.strip()  # Remove leading/trailing spaces
            output_name=output_name.split('.')[0]

            # Add ".pdf" extension if not provided
            if not output_name.endswith(".zip"):
                output_name += ".pdf"

        password1 = st.text_input("Enter your password:", type="password")
        
        if password1:
            st.info("Your Password is: "+password1)
            if st.button("Add Password"):
                encryption(password1,pdf_file_path,output_name)


if __name__=="__main__":
    atexit.register(remove_uploads_folder)
    main()
