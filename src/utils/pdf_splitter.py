import glob 
from chromadb.config import Settings
from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv


class DataExtractor:
    def __init__(self, pdf_directory):
        self.pdf_directory = pdf_directory
        self.pdf_text = []
        self.docs = []
        self.split_docs = None

    
    def extract_text(self):
        print(f'Extracting text from pdf files in {self.pdf_directory}')
        pdf_files = glob.glob(f'{self.pdf_directory}/*.pdf')
        print(pdf_files)
        for pdf_file in pdf_files:
            print(pdf_file)
            loader = PyPDFLoader(pdf_file)
            documents = loader.load()
            self.pdf_text.append(documents)

        return self.pdf_text


    # Function to clean and split text
    def clean_and_split_text(self, documents):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = []
        print(f'Cleaning and splitting text from {len(documents)} documents')
        for doc in documents:
            # Splitting each document individually
            split_docs.extend(splitter.split_documents(doc))
        print(f'Number of documents after splitting: {len(split_docs)}')
        return split_docs


