import os
from src.pdf_splitter import DataExtractor
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import chroma


class VectorDatabase:
    def __init__(self, db_name):
        self.db_name = "mental_health.db"
        self.persist_directory = os.path.join("../vector_embedding", db_name)  # creating vector database
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_key)

    # creating vector database for Mental Health Knowledge base
    def create_db(self, pdf_data):       
        self.vectDB = chroma.Chroma.from_documents(
                                                    pdf_data,
                                                    embedding=self.embeddings,
                                                    persist_directory=self.persist_directory
                                                    )
        self.vectDB.persist()

    # loading vector database for Mental Health Knowledge base
    def load_db(self):
        self.vectDB = chroma.Chroma.load(self.persist_directory)

# Example usage
def main():
    pdf_directory = './data/mental-health'
    data_extractor = DataExtractor(pdf_directory)
    text_data = data_extractor.extract_text()
    text_data = data_extractor.clean_and_split_text(text_data)
    
    # Step 2: Create and load the vector database
    vector_db = VectorDatabase(db_name="mental_health_vector_db")
    vector_db.create_db(text_data)
    vector_db.load_db()
    print("Vector embeddings have been generated and loaded successfully.")

if __name__ == "__main__":
    main()