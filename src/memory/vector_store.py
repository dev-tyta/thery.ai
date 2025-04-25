from pathlib import Path
from typing import List, Optional
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from src.llm.utils.logging import TheryBotLogger

class FAISSVectorSearch:
    def __init__(
        self,
        embedding_model: Optional[HuggingFaceEmbeddings] = None,
        db_path: Path = Path("vector_embedding/mental_health_vector_db"),
        k: int = 5,
        logger: Optional[TheryBotLogger] = None
    ):
        self.embedding_model = embedding_model or self._get_default_embedding_model()
        self.db_path = db_path
        self.k = k
        self.logger = logger or TheryBotLogger()
        self._initialize_store()
    
    def _get_default_embedding_model(self) -> HuggingFaceEmbeddings:
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={
                "padding": "max_length",
                "max_length": 512,
                "truncation": True,
                "normalize_embeddings": True
            }
        )
    
    def _initialize_store(self) -> None:
        if self.db_path.exists():
            self.vectorstore = FAISS.load_local(
                str(self.db_path),
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
        else:
            # Initialize with empty store
            self.vectorstore = FAISS.from_texts(
                [""], self.embedding_model
            )
    
    def search(self, query: str, k: Optional[int] = None) -> List[str]:
        try:
            results = self.vectorstore.similarity_search(
                query,
                k=(k or self.k)
            )
            return [res.page_content for res in results]
        except Exception as e:
            # Log error and return empty results
            self.logger.log_interaction(
                interaction_type="vector_search_error",
                data={"error": str(e)},
                level=logging.ERROR
            )
            return []
    
    def add_texts(self, texts: List[str]) -> None:
        """Add new texts to the vector store"""
        self.vectorstore.add_texts(texts)
        # Optionally save after adding
        self.save()
    
    def save(self) -> None:
        """Save the vector store to disk"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.vectorstore.save_local(str(self.db_path))