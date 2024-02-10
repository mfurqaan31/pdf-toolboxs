import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import atexit
import shutil
import requests

def check_encrypted(pdf_file_path):
    is_encrypted = False
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        is_encrypted = pdf_reader.is_encrypted

    return is_encrypted

def cleanup():
    # Delete 'uploads' folder when the application exits
    shutil.rmtree("uploads", ignore_errors=True)
    shutil.rmtree("faiss_index", ignore_errors=True)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks, api_key):
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}. If you do not have an API key, generate it from [here](https://makersuite.google.com/app/apikey)")
        st.stop()

def is_valid_api_key(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get("https://api.gemini.com/v1/symbols", headers=headers)
    if response.status_code == 200:
        return True
    else:
        return False

def get_conversational_chain(api_key, temperature):
    genai.configure(api_key=api_key)
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n
    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=temperature, google_api_key=api_key)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question, api_key, temperature):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    new_db = FAISS.load_local("faiss_index", embeddings)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain(api_key, temperature)
    st.write("Question: ", user_question)
    with st.spinner("Generating the answer..."):
        response = chain.invoke({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        st.write("Answer: ", response["output_text"])

def main():
    st.set_page_config("Chat PDF")
    st.header("Chat with PDF")

    # Create an "uploads" folder if it doesn't exist
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    pdf_doc = st.file_uploader("Upload your PDF File", type=["pdf"])
    if pdf_doc:
        # Save the uploaded PDF to the uploads folder
        pdf_path = os.path.join("uploads", pdf_doc.name)
        with open(pdf_path, "wb") as f:
            f.write(pdf_doc.getvalue())

        # Check if the uploaded PDF is encrypted
        if check_encrypted(pdf_path):
            st.error("The selected PDF is encrypted. Cannot process it.")
            st.stop()

        with st.spinner("Processing..."):
            raw_text = get_pdf_text([pdf_path])
            text_chunks = get_text_chunks(raw_text)
            api_key = st.text_input("Enter your Gemini API Key")
            if api_key:
                if is_valid_api_key(api_key):
                    get_vector_store(text_chunks, api_key)
                    st.success("PDF Processed Successfully")
                    
                    user_question = st.chat_input("Ask your question")
                    temperature = st.slider("Select Gemini LLM temperature", 0.0, 1.0, 0.3, 0.1)

                    if user_question:
                        user_input(user_question, api_key, temperature)
                else:
                    st.error("Invalid Gemini API Key. Please check your API key or create a new one at [here](https://makersuite.google.com/app/apikey)")
                    st.stop()
            else:
                st.error("Please enter your Gemini API Key")

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
