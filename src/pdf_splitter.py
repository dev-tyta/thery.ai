import os
from langchain.document_loaders import pdf
from langchain.text_splitter import TokenTextSplitter


class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.split_data = []
        self.pdf_content =None
        self.pdf_tokens = None

    def load_pdf(self):
        # checking for pdf files
        pdf_files = [os.path.join(root, file) for root, dirs, files in os.walk(pdf_path) for file in files if file.endswith(".pdf")]

        if not pdf_files:
            raise ValueError("No PDF files found in the provided directory.")

        # loading pdf content with Langchain PyPDFLoader
        for pdf_file in pdf_files:
            try:
                loader = pdf.PyPDFLoader(pdf_file)
                self.pdf_content = loader.load()
            except Exception as e:
                print(f"Error processing file {pdf_file}: {e}")

    def split_pdf_tokens(self):
        # splitting pdf content into tokens
        splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
        self.split_data.extend(splitter.split_documents(self.pdf_content))


        return self.split_data