# this skips all the encrypted pdfs
# multiple same pdfs cant be merged fix this
import streamlit as st
from streamlit_sortables import sort_items
import fitz
import io

def main():
    
    st.title("Merge PDFs")
    
    def is_encrypted(pdf_bytes):
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            encrypted = pdf_document.is_encrypted
            pdf_document.close()
            return encrypted
        except Exception as e:
            st.error(f"Error checking encryption status: {e}")
            return True  # Assume encrypted in case of an error

    def merge_pdf(uploaded_files, reordered_names, output_pdf_name):
        # Create a PDF writer object
        pdf_writer = fitz.open()

        # Iterate through the ordered PDF file names
        for pdf_name in reordered_names:
            # Get the full path of the PDF file
            pdf_path = [file.name for file in uploaded_files if file.name == pdf_name][0]
            
            # Read the PDF file
            pdf_bytes = [file.read() for file in uploaded_files if file.name == pdf_path][0]
            
            if is_encrypted(pdf_bytes):
                st.warning(f"{pdf_path}"+" is encrypted, hence will not be considered for merging")
                continue

            # Insert the PDF pages into the PDF writer
            try:
                pdf_writer.insert_pdf(fitz.open(stream=pdf_bytes, filetype="pdf"), from_page=0, to_page=-1)
            except ValueError as e:
                st.error(f"Error adding {pdf_path} to the merged PDF: {e}")

        # Save the merged PDF to a BytesIO object
        merged_pdf_io = io.BytesIO()
        pdf_writer.save(merged_pdf_io)
        pdf_writer.close()

        st.success("The PDFs has been merged, and it is ready for download.")
        # Display a download button for the merged PDF
        st.download_button(
            label="Download PDF",
            data=merged_pdf_io.getvalue(),
            file_name=output_pdf_name,
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
        st.write("Order for the uploaded PDF files:")
        
        # Display the names with the selected order
        for index, name in enumerate(reordered_names):
            st.write(f"{index + 1}. {name}")
        
        # Allow the user to enter the name of the output PDF
        output_pdf_name = st.text_input("Enter the name of the output PDF file (without extension):", "merged_pdf")

        if st.button("Merge Pdfs"):
            merge_pdf(uploaded_files, reordered_names, f"{output_pdf_name}.pdf")

if __name__ == "__main__":
    main()
