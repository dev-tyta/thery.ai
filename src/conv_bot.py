import os
from langchain_community.llms.ollama import Ollama 
from langchain_chroma import Chroma
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from dotenv import load_dotenv


load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")


llm = Ollama(model="llama3")
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"padding": "max_length",
                 "max_length": 512,
                 "truncation": True,
                 "normalize_embeddings": True
                }

embeddings = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
)

vectorstore = Chroma(persist_directory="./vector_embedding/mental_health_vector_db", embedding_function=embeddings)

retriever = vectorstore.as_retriever(search_type="similarity", top_k=5)
query = "What is mental health?"

response = retriever.invoke(query)

print(response)