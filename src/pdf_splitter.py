import os
import openai
import langchain
import tiktoken
import chromadb


from langchain.document_loaders import unstructured, pdf
from langchain.text_splitter import TokenTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import chroma
from langchain.llms import openai
from langchain.chains import conversational_retrieval



def get_pdf_tokens(pdf_path):
    # checking for pdf files
    for file in os.listdir(pdf_path):
        if file.endswwith(".pdf"):
            pdf_path = os.path.join(pdf_path, file)

    # loading pdf content with Langchain PyPDFLoader
    load = pdf.PyPDFLoader(pdf_path)
    pdf_content = load.load()

    # splitting pdf content into tokens
    splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
    splitData = splitter.split_documents(pdf_content)

    return splitData

