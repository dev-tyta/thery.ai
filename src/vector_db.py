import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import chroma


class VectorDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.persist_directory = os.path.join("../vector_embedding", db_name)  # creating vector database
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_key)

    # creating vector database for Mental Health Knowledge base
    def create_db(self, pdf_data):       
        self.vectDB = chroma.Chroma.from_documents(pdf_data,self.embeddings,
                                            collection_name= self.db_name,
                                            persist_directory=self.persist_directory
                                            )
        self.vectDB.persist()

    # loading vector database for Mental Health Knowledge base
    def load_db(self):
        self.vectDB = chroma.Chroma.load(self.persist_directory)
