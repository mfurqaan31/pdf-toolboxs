# encrypyed pdfs need to be fixed
import streamlit as st
from streamlit_sortables import sort_items
import fitz
import io

def main():
    
    st.title("PDF File Uploader")
    
    def merge_pdf(uploaded_files, reordered_names):
        # Create a PDF writer object
        pdf_writer = fitz.open()

        # Iterate through the ordered PDF file names
        for pdf_name in reordered_names:
            # Get the full path of the PDF file
            pdf_path = [file.name for file in uploaded_files if file.name == pdf_name][0]
            
            # Read the PDF file
            pdf_bytes = [file.read() for file in uploaded_files if file.name == pdf_path][0]
            
            # Add the PDF to the PDF writer object
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            pdf_writer.insert_pdf(pdf_document)
        
        # Save the merged PDF to a BytesIO object
        merged_pdf_io = io.BytesIO()
        pdf_writer.save(merged_pdf_io)
        pdf_writer.close()

        # Display a download button for the merged PDF
        st.download_button(
            label="Download Merged PDF",
            data=merged_pdf_io.getvalue(),
            file_name="merged_pdf.pdf",
            key="merged_pdf_button"
        )

    # Create a button to add PDF files
    uploaded_files = st.file_uploader("Add PDF files", type="pdf", accept_multiple_files=True)

    # Display the names of the uploaded PDF files
    if uploaded_files:
        
        # Display the names in a multiselect for rearranging
        file_names = [file.name for file in uploaded_files]
        st.write("Arrange the order of the pdf")
        reordered_names = sort_items(file_names)
        st.write("Uploaded PDF Files:")
        
        # Display the names with the selected order
        for index, name in enumerate(reordered_names):
            st.write(f"{index + 1}. {name}")
        
        if st.button("Merge Pdfs"):
            merge_pdf(uploaded_files, reordered_names)

if __name__ == "__main__":
    main()
