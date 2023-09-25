from typing import Any
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
import gradio as gr
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Milvus


MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

class MyApp:
    def __init__(self) -> None:
        self.chain = None
        self.chat_history: list = []
        self.previous_extension = None

    def __call__(self, files: list) -> Any:
        self.chain = self.build_chain(files)
        self.previous_extension = None
        return self.chain
    
    def process_files(self, files: list):
        loaded_files = set()
        documents = []
        for file in files:
            tmp_file = file.name
            file_extension = tmp_file.split(".")[-1]

            # Check if the file has already been loaded
            if tmp_file in loaded_files:
                continue

            if self.previous_extension is not None and self.previous_extension != file_extension:
                raise gr.Error('You can load PDF files, Doc files, or text files separately.')

            if tmp_file.endswith(".pdf"):
                loader = PyPDFLoader(file.name)
                documents.extend(loader.load())
            elif tmp_file.endswith('.docx') or tmp_file.endswith('.doc'):
                loader = Docx2txtLoader(file.name)
                documents.extend(loader.load())
            elif tmp_file.endswith('.txt'):
                loader = TextLoader(file.name)
                documents.extend(loader.load())

            # Update the previous_extension
            self.previous_extension = file_extension

            # Add the loaded file to the set to prevent loading it again
            loaded_files.add(tmp_file)

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
        documents = text_splitter.split_documents(documents)

        return documents
    
    def build_chain(self, files: list):
        documents = self.process_files(files)
        # Load embeddings model
        embeddings = OpenAIEmbeddings() 
        vector_db = Milvus.from_documents(
            documents,
            embedding=embeddings,
            connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT},
            drop_old=True)
        chain = ConversationalRetrievalChain.from_llm(
            ChatOpenAI(temperature=0.3), 
            retriever=vector_db.as_retriever(search_kwargs={"k": 2}),
            return_source_documents=True,)
        return chain


