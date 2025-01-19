from langchain_openai import ChatOpenAI  # Changed to ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any
import os
import sys
import faulthandler
faulthandler.enable()


class EmotionDetector:
    def __init__(self, api_key: str):
        """Initialize the emotion detector with OpenAI API key."""
        if not api_key:
            raise ValueError("API key cannot be empty")
            
        os.environ["OPENAI_API_KEY"] = api_key
        try:
            self.llm = ChatOpenAI(
                temperature=0.3,
                model_name="gpt-3.5-turbo",
                max_tokens=150  # Add token limit for safety
            )
        except Exception as e:
            print(f"Error initializing ChatOpenAI: {str(e)}")
            sys.exit(1)
        
        # Create a prompt template for emotion detection
        self.prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze the emotional content in the following text and return the primary emotion:
            Text: {text}
            Primary emotion:"""
        )
        print(f"Prompt created: {self.prompt}")
        
        # Create the chain with error handling
        try:
            self.chain = self.prompt | self.llm # LLMChain(llm=self.llm, prompt=self.prompt)
            print("LLMChain created successfully")
        except Exception as e:
            print(f"Error creating LLMChain: {str(e)}")
            sys.exit(1)
    
    def detect_emotion(self, text: str) -> str:
        """Detect the primary emotion in the given text."""
        if not text:
            return "Error: Empty text provided"
            
        try:
            print("Invoking emotion detection chain")
            response = self.chain.invoke(text)
            print(f"Response received: {response}")
            return response.strip()
        except Exception as e:
            return f"Error detecting emotion: {str(e)}"

    def get_detailed_analysis(self, text: str) -> Dict[str, Any]:
        """Get a more detailed emotional analysis of the text."""
        if not text:
            return {"analysis": "Error: Empty text provided"}
        print("Creating detailed analysis chain")
        detailed_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            Provide a detailed emotional analysis of the following text:
            Text: {text}
            Please analyze:
            1. Primary emotion
            2. Intensity (1-10)
            3. Secondary emotions
            Analysis:"""
        )
        print(f"Detailed analysis chain created: {detailed_prompt}")
        
        try:
            chain = detailed_prompt | self.llm  # LLMChain(llm=self.llm, prompt=detailed_prompt)
            print("Chain created")
            response = chain.invoke(text)
            print(f"Response received: {response}")
            return {"analysis": response.strip()}
        except Exception as e:
            return {"analysis": f"Error in detailed analysis: {str(e)}"}

def main():
    # Example usage with proper error handling
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
        
    try:
        detector = EmotionDetector(api_key)
        print("Model Loaded Successfully")
        
        sample_text = "I'm really excited about this new project!"
        print(f"Sample text: {sample_text}")
        emotion = detector.detect_emotion(sample_text)
        print(f"Detected emotion: {emotion}")
        
        detailed = detector.get_detailed_analysis(sample_text)
        print(f"Detailed analysis: {detailed}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()