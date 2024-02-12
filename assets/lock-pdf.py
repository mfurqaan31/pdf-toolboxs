# main code
import streamlit as st
import PyPDF2
import os, io, shutil, atexit

def check_encrypted(pdf_file_path):
    is_encrypted = False
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        is_encrypted = pdf_reader.is_encrypted

    if is_encrypted:
        st.error("The selected PDF is encrypted.")
        st.stop()

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)

def encryption(password, file_path, output_name):
    pdf_writer = PyPDF2.PdfWriter()
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
    pdf_writer.encrypt(user_password=password, owner_pwd=None, use_128bit=True)
    encrypt_pdf_io = io.BytesIO()
    pdf_writer.write(encrypt_pdf_io)
    encrypt_pdf_io.seek(0)
    st.success("The PDF has been encrypted and is ready for download.")
    st.download_button(
        label="Download PDF",
        data=encrypt_pdf_io.getvalue(),
        file_name=output_name,
        mime="application/pdf",
        key="encrypt_pdf_button"
    )

def main():
    st.title("PDF Encrypter 🔒")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file:
        pdf_file_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(pdf_file_path, 'wb') as pdf_file:
            pdf_file.write(uploaded_file.read())
        check_encrypted(pdf_file_path)
        password1 = st.text_input("Enter your password:", type="password")
        if password1:
            st.info("Your Password is: "+password1)
            output_name = st.text_input("Enter the PDF file name (without extension):", "output", key="output_name")
            if output_name:
                output_name = output_name.strip()
                output_name = output_name.split('.')[0]
                if not output_name.endswith(".zip"):
                    output_name += ".pdf"
            if st.button("Add Password"):
                encryption(password1,pdf_file_path,output_name)

if __name__=="__main__":
    atexit.register(cleanup)
    main()
