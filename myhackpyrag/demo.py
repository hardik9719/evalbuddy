import streamlit as st
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Setup Streamlit interface
st.title("Chat with Webpage 🌐")
st.caption("This app allows you to chat with a webpage using local Llama-2 and RAG")

# Add Python code analysis section
python_code = st.text_area("Enter Python code to analyze", height=200)
analyze_button = st.button("Analyze Code")

if analyze_button and python_code:  # Only run analysis when button is clicked and code exists
    prompt = f"""Analyze this Python code and provide:
    1. Brief summary
    2. Main functionality
    3. Key components/libraries used
    4. Potential improvements (if any)
    
    Code:
    {python_code}"""
    
    with st.spinner('Analyzing code...'):  # Add loading indicator
        response = ollama.chat(model='llama2', messages=[{'role': 'user', 'content': prompt}])
        
        with st.card("Code Analysis Summary"):
            st.markdown(response['message']['content'])
            st.divider()
            st.caption("Analysis provided by Llama-2")

# Get webpage URL input
webpage_url = st.text_input("Enter Webpage URL", type="default")

if webpage_url:
    # Load and process webpage data
    loader = WebBaseLoader(webpage_url)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=10)
    splits = text_splitter.split_documents(docs)

    # Create embeddings and vector store
    embeddings = OllamaEmbeddings(model="llama3.2")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

    # Define Llama-3 model function
    def ollama_llm(question, context):
        formatted_prompt = f"Question: {question}\n\nContext: {context}"
        response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': formatted_prompt}])
        return response['message']['content']

    # Setup RAG chain
    retriever = vectorstore.as_retriever()

    def combine_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def rag_chain(question):
        retrieved_docs = retriever.invoke(question)
        formatted_context = combine_docs(retrieved_docs)
        return ollama_llm(question, formatted_context)

    st.success(f"Loaded {webpage_url} successfully!")

    # Chat interface
    prompt = st.text_input("Ask any question about the webpage")
    if prompt:
        result = rag_chain(prompt)
        st.write(result)
