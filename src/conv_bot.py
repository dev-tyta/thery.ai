import os
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.llms.openai import OpenAI
from langchain.memory import ConversationBufferMemory 
from dotenv import load_dotenv

load_dotenv()

class ChatChain:
    def __init__(self, vectdb):
        self.memory = ConversationBufferMemory(memory_key="chat_history",  return_messages=True)
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.vectdb = vectdb
        self.chat_history = []

    def initializing_retrieval(self):
        chat_retrieval = ConversationalRetrievalChain.from_llm(
            OpenAI(openai_api_key=self.openai_key, temperature= 0.8,
                   model_name="gpt-3.5-turbo"),
            self.vectdb.as_retriever(),
            memory = self.memory
                   )
        return chat_retrieval

    def process_chat(self, user_input):
        chat_retrieval = self.initializing_retrieval()
        while user_input != "send":
            user_input = user_input
            if user_input != exit:
                response = chat_retrieval({"question":user_input, "chat_history":self.chat_history})
                return response
            

