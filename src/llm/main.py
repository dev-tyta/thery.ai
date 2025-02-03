import logging
from src.llm.agents.conversation_agent import ConversationAgent
from src.llm.utils.logging import TheryBotLogger
from src.llm.core.config import settings

def main():
    # Initialize logger
    logger = TheryBotLogger()
    
    # Initialize main conversation agent
    agent = ConversationAgent()
    
    # Example interaction
    query = "But I have been try to do this for quite a while now and I am still not able to get it right."
    
    try:
        # Process query
        response = agent.process(query)
        
        # Log interaction
        logger.log_interaction(
            interaction_type="user_interaction",
            data={
                "query": query,
                "response": response.response,
                "status": "success"
            },
            level=logging.INFO
        )
        
        # Print response
        print(f"Thery AI: {response.response}")
        
    except Exception as e:
        logger.log_interaction(
            interaction_type="error",
            data={
                "query": query,
                "error": str(e)
            },
            level=logging.ERROR
        )
        print("An error occurred. Please try again.")

if __name__ == "__main__":
    main()