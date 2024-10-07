import os
import PyPDF2
import glob 
import openai
import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv


load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


class DataExtractor:
    def __init__(self, pdf_directory):
        self.pdf_directory = pdf_directory
        self.pdf_text = []
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


    def clean_and_split_text(self, text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                       chunk_overlap=200,
                                                       length_function=len,)
        self.split_docs = text_splitter.split_documents(text)  
        
        return self.split_docs



# testing class DataExtractor
if __name__ == '__main__':
    pdf_directory = './data/mental-health'
    data_extractor = DataExtractor(pdf_directory)
    pdf_text = data_extractor.extract_text()
    print(pdf_text)
    split_docs = data_extractor.clean_and_split_text(pdf_text)
    print(split_docs)
    print(len(split_docs))
    print(type(split_docs))