import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import chroma


# creating vector database for Mental Health Knowledge base
def create_db(pdf_data, db_name):
    # creating vector database

    persist_directory = os.path.join("../vector_embedding", db_name)

    openai_key = os.environ.get("OPENAI_API_KEY")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
    vectDB = chroma.Chroma.from_documents(pdf_data, embeddings,
                                          collection_name= db_name,
                                          persist_directory=persist_directory
                                          )
    
    vectDB.persist()
    
    

