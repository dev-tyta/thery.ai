import os
from src.utils.pdf_splitter import DataExtractor
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import chroma


class VectorDatabase:
    def __init__(self, db_name):
        self.db_name = "mental_health.db"
        self.persist_directory = os.path.join("../vector_embedding", db_name)  # creating vector database      
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.model_kwargs = {"device": "cpu"}
        self.encode_kwargs = {"padding": "max_length",
                              "max_length": 512,
                              "truncation": True,
                              "normalize_embeddings": True
                              }
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=self.model_name,
            model_kwargs=self.model_kwargs,
            encode_kwargs=self.encode_kwargs
)

    # creating vector database for Mental Health Knowledge base
    def create_db(self, pdf_data):       
        self.vectDB = chroma.Chroma.from_documents(
                                                    pdf_data,
                                                    embedding=self.embeddings,
                                                    persist_directory=self.persist_directory
                                                    )
        self.vectDB.add_documents(pdf_data)
        self.vectDB.persist()


def main():
    pdf_directory = './data/mental-health'
    data_extractor = DataExtractor(pdf_directory)
    text_data = data_extractor.extract_text()
    text_data = data_extractor.clean_and_split_text(text_data)
    
    # Step 2: Create and load the vector database
    vector_db = VectorDatabase(db_name="mental_health_vector_db")
    vector_db.create_db(text_data)
    print("Vector embeddings have been generated and loaded successfully.")

if __name__ == "__main__":
    main()