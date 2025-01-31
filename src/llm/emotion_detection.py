# from langchain_openai import ChatOpenAI  # Changed to ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional
import os
import sys
from src.llm.core import TheTherapistLLM
from src.memory.history import History
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


class EmotionDetector:
    def __init__(self, 
                llm: Optional['TheTherapistLLM'] = None,
                history: Optional['History'] = None,

                ):
        """Initialize the emotion detector with OpenAI API key."""
        self.llm = llm or TheTherapistLLM()
        self.history = history or History()

    @staticmethod
    def _construct_prompt(text: str) -> str:
        # Create a prompt template for emotion detection
        prompt = f"""
            Analyze the emotional content in the following text and return the primary emotion:
            Text: {text}
            Primary emotion:"""
        print(f"Prompt created: {prompt}")

        return prompt
    
    def detect_emotion(self, text: str) -> str:
        """Detect the primary emotion in the given text."""
        if not text:
            return "Error: Empty text provided"
        prompt = self._construct_prompt(text)
        try:
            print("Invoking emotion detection chain")
            
            response = self.llm.generate(prompt)
            print(f"Response received: {response}")
            return response.content.strip()
        except Exception as e:
            return f"Error detecting emotion: {str(e)}"

    def get_detailed_analysis(self, text: str) -> Dict[str, Any]:
        """Get a more detailed emotional analysis of the text."""
        if not text:
            return {"analysis": "Error: Empty text provided"}
        
        detailed_prompt =f"""
            Provide a detailed emotional analysis of the following text:
            Text: {text}
            Please analyze:
            1. Primary emotion
            2. Intensity (1-10)
            3. Secondary emotions
            Analysis:"""
        print(f"Detailed analysis chain created: {detailed_prompt}")
        
        try:
            response = self.llm.generate(prompt=detailed_prompt)
            print(f"Response received: {response}")
            return {"analysis": response.content.strip()}
        except Exception as e:
            return {"analysis": f"Error in detailed analysis: {str(e)}"}

def main():
    # Example usage with proper error handling        
    try:
        detector = EmotionDetector()
        print("Model Loaded Successfully")
        
        sample_text = "I'm really excited about this new project!"
        print(f"Sample text: {sample_text}")
        emotion = detector.detect_emotion(text=sample_text)
        print(f"Detected emotion: {emotion}")
        
        detailed = detector.get_detailed_analysis(text=sample_text)
        print(f"Detailed analysis: {detailed}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()