import os
from src.utils.pdf_splitter import DataExtractor
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import FAISS # Fixed import

class VectorDatabase:
    def __init__(self, db_name):
        self.db_name = db_name  # Use parameter
        self.persist_directory = os.path.join("vector_embedding", self.db_name)  # Fixed path
        
        # Correct embeddings for sentence-transformers model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={
                "padding": "max_length",
                "max_length": 512,
                "truncation": True,
                "normalize_embeddings": True
            }
        )

    def create_db(self, pdf_data):
        # Create and persist database in one step
        self.vectDB = FAISS.from_documents(
            documents=pdf_data,
            embedding=self.embeddings
        )
        self.vectDB.save_local(self.persist_directory)
        # No need for add_documents() or explicit persist() when using from_documents

def main():
    pdf_directory = './data/mental_health'
    data_extractor = DataExtractor(pdf_directory)
    text_data = data_extractor.extract_text()
    text_data = data_extractor.clean_and_split_text(text_data)
    
    # Step 2: Create and load the vector database
    vector_db = VectorDatabase(db_name="mental_health_vector_db")
    vector_db.create_db(text_data)
    print("Vector embeddings have been generated and loaded successfully.")

if __name__ == "__main__":
    main()