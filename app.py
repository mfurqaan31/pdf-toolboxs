import streamlit as st
import importlib.util
import atexit,shutil

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)
    shutil.rmtree("faiss_index", ignore_errors=True)
    shutil.rmtree("./assets/uploads", ignore_errors=True)
    shutil.rmtree("./assets/faiss_index", ignore_errors=True)
    shutil.rmtree("./assets/__pycache__", ignore_errors=True)

def main():
    st.set_page_config("pdf-toolboxz")
    st.title("PDF Toolboxz 📄 🛠")
    
    st.sidebar.title('PDF Tools')

    page = st.sidebar.radio('Navigate', ['Home','View PDF','Merge PDF', 'Split PDF', 'PDF to Images', 'Images to PDF', 'Encrypt PDF', 'Decrypt PDF','Chat with PDF'])

    if page == 'Home':
        home = import_module('home')
        home.main()

    elif page == 'View PDF':
        view_pdf = import_module('view-pdf')
        view_pdf.main()

    elif page == 'Merge PDF':
        merge_pdf = import_module('merge-pdf')
        merge_pdf.main()

    elif page == 'Split PDF':
        split_pdf = import_module('split-pdf')
        split_pdf.main()

    elif page == 'Images to PDF':
        img_pdf = import_module('img-to-pdf')
        img_pdf.main()

    elif page == 'PDF to Images':
        pdf_pdf = import_module('pdf-to-img')
        pdf_pdf.main()

    elif page == 'Encrypt PDF':
        lock_pdf = import_module('lock-pdf')
        lock_pdf.main()

    elif page == 'Decrypt PDF':
        unlock_pdf = import_module('unlock-pdf')
        unlock_pdf.main()

    elif page == 'Chat with PDF':
        chat_pdf = import_module('chat-pdf')
        chat_pdf.main()
        
def import_module(module_name):
    spec = importlib.util.spec_from_file_location(module_name, f"assets/{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

if __name__ == "__main__":
    atexit.register(cleanup)
    main()