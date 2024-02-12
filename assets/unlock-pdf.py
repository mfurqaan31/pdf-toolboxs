# main code
import streamlit as st
import PyPDF2
import os, io, shutil, atexit

def check_encrypted(pdf_file_path):
    is_encrypted = False
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        is_encrypted = pdf_reader.is_encrypted

    if not is_encrypted:
        st.error("The selected PDF is not encrypted.")
        st.stop()

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)

def decryption(password, file_path, output_name):
    pdf_writer = PyPDF2.PdfWriter()
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        if pdf_reader.decrypt(password):
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            decrypted_pdf_io = io.BytesIO()
            pdf_writer.write(decrypted_pdf_io)
            decrypted_pdf_io.seek(0)
            st.success("The PDF has been decrypted and is ready for download.")
            st.download_button(
                label="Download PDF",
                data=decrypted_pdf_io.getvalue(),
                file_name=output_name,
                mime="application/pdf",
                key="decrypt_pdf_button"
            )
        else:
            st.error("Incorrect password. Please try again.")

def main():
    st.title("PDF Decrypter 🔓")
    uploaded_file = st.file_uploader("Choose an encrypted PDF file", type="pdf")
    if uploaded_file:
        pdf_file_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(pdf_file_path, 'wb') as pdf_file:
            pdf_file.write(uploaded_file.read())
        check_encrypted(pdf_file_path)
        password = st.text_input("Enter the password to decrypt the PDF:", type="password")
        if password:
            output_name = st.text_input("Enter the PDF file name (without extension):", "decrypted_output", key="output_name")
            if output_name:
                output_name = output_name.strip()
                if not output_name.endswith(".pdf"):
                    output_name += ".pdf"
            if st.button("Decrypt PDF"):
                if output_name:  
                    decryption(password, pdf_file_path, output_name)

if __name__=="__main__":
    atexit.register(cleanup)
    main()
