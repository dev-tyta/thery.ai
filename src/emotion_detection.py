from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any
import os

class EmotionDetector:
    def __init__(self, api_key: str):
        """Initialize the emotion detector with OpenAI API key."""
        os.environ["OPENAI_API_KEY"] = api_key
        self.llm = OpenAI(temperature=0.3)
        
        # Create a prompt template for emotion detection
        self.prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze the emotional content in the following text and return the primary emotion:
            Text: {text}
            Primary emotion:"""
        )
        
        # Create the chain
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def detect_emotion(self, text: str) -> str:
        """Detect the primary emotion in the given text."""
        try:
            response = self.chain.run(text)
            return response.strip()
        except Exception as e:
            return f"Error detecting emotion: {str(e)}"

    def get_detailed_analysis(self, text: str) -> Dict[str, Any]:
        """Get a more detailed emotional analysis of the text."""
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
        
        chain = LLMChain(llm=self.llm, prompt=detailed_prompt)
        response = chain.run(text)
        return {"analysis": response.strip()}

if __name__ == "__main__":
    # Example usage
    api_key = os.getenv("OPENAI_API_KEY")
    detector = EmotionDetector(api_key)
    
    sample_text = "I'm really excited about this new project!"
    emotion = detector.detect_emotion(sample_text)
    print(f"Detected emotion: {emotion}")
    
    detailed = detector.get_detailed_analysis(sample_text)
    print(f"Detailed analysis: {detailed}")