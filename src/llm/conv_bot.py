import os
from langchain_community.llms.ollama import Ollama 
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings                       
from langchain_chroma import Chroma
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

from typing import Annotated, Sequence, Literal, List
from typing_extensions import TypedDict


load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "THETHERAPAIST Chatbot"


class TheTherapistLLM:
    def __init__(self):
        self.llm = Ollama(model="llama3")
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.model_kwargs = {"device": "cpu"}
        self.encode_kwargs = {"padding": "max_length",
                        "max_length": 512,
                        "truncation": True,
                        "normalize_embeddings": True
                        }

    def initialize_tools(self):
        tavily_tool = [
            TavilySearchResults(
                max_results=3, 
                name="tavily_search",
                include_answer=True,
                include_images=True,
                include_depth="advanced"
                )
        ]
        
        @tool()
        def vector_db_search(
            self,
            query: Annotated[str, "The query to search in the vector database."]
        ): 
            embeddings = HuggingFaceBgeEmbeddings(
                    model_name=self.model_name,
                    model_kwargs=self.model_kwargs,
                    encode_kwargs=self.encode_kwargs
                    )
            vectorstore = Chroma(persist_directory="./vector_embedding/mental_health_vector_db", embedding_function=embeddings)

            results = vectorstore.similarity_search(query, k=5)
            return "\n".join([res.page_content for res in results])
        
        return tavily_tool, vector_db_search
    

# test class
llm = TheTherapistLLM()