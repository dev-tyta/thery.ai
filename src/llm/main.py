import logging
from src.llm.agents.conversation_agent import ConversationAgent
from src.llm.utils.logging import TherapyBotLogger
from src.llm.core.config import settings

def main():
    # Initialize logger
    logger = TherapyBotLogger()
    
    # Initialize main conversation agent
    agent = ConversationAgent()
    
    # Example interaction
    query = "I've been feeling overwhelmed with work lately"
    
    try:
        # Process query
        response = agent.process(query)
        
        # Log interaction
        logger.log_interaction(
            "user_interaction",
            {
                "query": query,
                "response": response.dict(),
                "status": "success"
            }
        )
        
        # Print response
        print(f"Bot: {response.response}")
        
    except Exception as e:
        logger.log_interaction(
            "error",
            {
                "query": query,
                "error": str(e)
            },
            level=logging.ERROR
        )
        print("An error occurred. Please try again.")

if __name__ == "__main__":
    main()