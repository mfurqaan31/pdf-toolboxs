import streamlit as st

def main():
    st.markdown("### Home Page")

    st.write("""
            This application provides various tools for manipulating PDF files:
             
            - View PDF: Upload a single PDF and the pages of the PDF will de displayed. Please ensure the PDF is not encrypted.

            - Merge PDF: Upload multiple PDFs and arrange their order in the select box. The uploaded PDFs will be merged according to the selected order. Please ensure that none of the PDFs are encrypted.

            - Split PDF: Upload a single PDF, split its pages into ranges, and download the resulting ZIP file containing the split PDF ranges, or merge the ranges into a single PDF. Please ensure the PDF is not encrypted.

            - Images to PDF: Upload multiple images, arrange their order in the select box, and merge them into a single PDF.

            - PDF to Image: Upload a single PDF, and its pages will be converted to images and available for download as a ZIP file. Please ensure the PDF is not encrypted.

            - Encrypt PDF: Upload a single non-encrypted PDF and add a password to protect it. Please ensure the PDF is not already encrypted.

            - Decrypt PDF: Upload a single encrypted PDF, enter the password, and download the decrypted PDF. Please ensure the PDF is encrypted.

            - Chat with PDF: Upload a single non-encrypted PDF, enter your valid Gemini-pro API key, and ask questions related to the PDF in the chat input. You will receive answers accordingly.
            """)

    st.write("Developed my Mohammed Furqaan")

if __name__=="__main__":
    main()