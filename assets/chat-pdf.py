# Using multiple models for LLM
import streamlit as st
from PyPDF2 import PdfReader
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_groq import ChatGroq
import atexit, shutil, os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def check_encrypted(pdf_file_path):
    is_encrypted = False
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        is_encrypted = pdf_reader.is_encrypted
    return is_encrypted

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)

def process_pdf_and_initialize_chatbot(uploaded_file, slider, llm_model):
    with st.spinner("Processing the pdf..."):
        pdf_text = ""
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        Texts = text_splitter.split_text(pdf_text)
        
        embeddings = GoogleGenerativeAIEmbeddings(google_api_key=st.secrets["GEMINI_API_KEY"], model="models/text-embedding-004")
        
        docsearch = FAISS.from_texts(Texts, embeddings)
        
        message_history = ChatMessageHistory()
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            chat_memory=message_history,
            return_messages=True,
        )
    
        groq_ai = ChatGroq(
            groq_api_key=st.secrets["GROQ_API_KEY"],
            model_name=llm_model,
            temperature=slider
        )
        
        chain = ConversationalRetrievalChain.from_llm(
            llm=groq_ai,
            chain_type="stuff",
            retriever=docsearch.as_retriever(),
            memory=memory,
            return_source_documents=True,
        )
    
    st.success("PDF Processed Successfully generating the answer...")
    return chain
    

def main():
    st.header("Chat with PDF 💬")
    
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
        
    uploaded_file = st.file_uploader("Please upload a PDF file to begin!", type="pdf")

    if uploaded_file:
        pdf_path = os.path.join("uploads", uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if check_encrypted(pdf_path):
            st.error("The selected PDF is encrypted. Cannot process it.")
            st.stop()
        
        llm_options = ["llama3-8b-8192",
                       "gemma-7b-it",
                       "mixtral-8x7b-32768",
                       "llama3-70b-8192"]
        llm_model = st.selectbox("Select the LLM model", llm_options, index=0)
        
        slider = st.slider("Select LLM temperature", 0.0, 1.0, 0.3, 0.1)
        
        user_question = st.chat_input("Ask your question here:")
        
        if user_question:
            try:
                chain= process_pdf_and_initialize_chatbot(pdf_path, slider, llm_model)
                res = chain.invoke(user_question)
                answer = res["answer"]
                st.write("Question:", user_question)
                st.write("Answer:", answer)
            except Exception as e:
                if "model_not_active" in str(e):
                    st.error("The selected LLM model is not active. Please choose a different model.")
                    
                else:
                    st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
