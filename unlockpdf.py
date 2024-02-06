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

    return is_encrypted

def remove_uploads_folder():
    # Remove the "uploads" folder when the program exits
    shutil.rmtree("uploads", ignore_errors=True)

def decryption(password, file_path, output_name):
    # Create a PdfReader to read the encrypted PDF
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Check if the provided password is correct
        if not pdf_reader.decrypt(password):
            st.error("Incorrect password. Please try again.")
            return

        # Create a PdfWriter to write the decrypted PDF
        pdf_writer = PyPDF2.PdfWriter()

        # Add each page to the writer
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # Write the decrypted PDF to a BytesIO buffer
        decrypted_pdf_io = io.BytesIO()
        pdf_writer.write(decrypted_pdf_io)

        # Seek to the beginning of the BytesIO buffer
        decrypted_pdf_io.seek(0)

        # Success message and download button
        st.success("The PDF has been decrypted and is ready for download.")
        st.download_button(
            label="Download Decrypted PDF",
            data=decrypted_pdf_io.getvalue(),
            file_name=output_name,
            mime="application/pdf",
            key="decrypt_pdf_button"
        )

def main():
    st.title("PDF Decrypter")

    uploaded_file = st.file_uploader("Choose an encrypted PDF file", type="pdf")

    if uploaded_file:
        pdf_file_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)

        with open(pdf_file_path, 'wb') as pdf_file:
            pdf_file.write(uploaded_file.read())

        is_encrypted = check_encrypted(pdf_file_path)

        if not is_encrypted:
            st.error("The selected PDF is not encrypted.")
            st.stop()

        output_name = st.text_input("Enter the decrypted PDF file name (without extension):", "decrypted_output", key="output_name")

        # Check if the user has entered a PDF file name
        if output_name:
            output_name = output_name.strip()  # Remove leading/trailing spaces
            output_name += ".pdf"

        password1 = st.text_input("Enter the password to decrypt the PDF:", type="password")
        
        if password1:
            if st.button("Decrypt PDF"):
                decryption(password1, pdf_file_path, output_name)

if __name__=="__main__":
    atexit.register(remove_uploads_folder)
    main()
