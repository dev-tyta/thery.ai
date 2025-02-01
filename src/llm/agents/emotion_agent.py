import textwrap
from typing import Dict, Any
import logging
from .base_agent import BaseAgent
from src.llm.models.schemas import EmotionalAnalysis

class EmotionAgent(BaseAgent):
    def process(self, text: str) -> EmotionalAnalysis:
        """Process text for emotional content"""
        prompt = self._construct_emotion_prompt(text)
        response = self.llm.generate(prompt)
        analysis = self._parse_emotion_response(response.content)
        self._log_action(action="emotion_analysis", metadata={"text": text, "analysis": analysis}, level=logging.INFO)
        
        return EmotionalAnalysis(
            primary_emotion=analysis['primary_emotion'],
            intensity=analysis['intensity'],
            secondary_emotions=analysis['secondary_emotions'],
            triggers=analysis['emotional_triggers'],
            coping_strategies=analysis['coping_strategies'],
            confidence_score=analysis['confidence_score']
        )
    
    def _construct_emotion_prompt(self, text: str) -> str:
        emotion_prompt = f"""
            Analyze the emotional content in the following text:
            Text: {text}
            
            Provide analysis in the following format:
            1. Primary emotion: [single emotion]
            2. Intensity: [number between 1 and 10]
            3. Secondary emotions: [comma-separated list of emotions]
            4. Emotional triggers: [comma-separated list of triggers]
            5. Suggested coping strategies: [comma-separated list of strategies]
            6. Confidence score: [number between 0 and 1]
            
            Example:
            1. Primary emotion: Anxiety
            2. Intensity: 7
            3. Secondary emotions: Fear, Worry
            4. Emotional triggers: Work deadline, Family conflict
            5. Suggested coping strategies: Deep breathing, Journaling, Talking to a friend
            6. Confidence score: 0.8
        """
        
        return textwrap.dedent(emotion_prompt).strip()
    
    def _parse_emotion_response(self, response: str) -> dict:
        try:
            analysis = {
                'primary_emotion': '',
                'intensity': 0,
                'secondary_emotions': [],
                'emotional_triggers': [],
                'coping_strategies': [],
                'confidence_score': 0.0
            }
            
            for line in response.split('\n'):
                # Convert the line to string explicitly in case it's not
                line = str(line).strip()
                if not line:
                    continue
                    
                # Split on first colon only
                parts = line.split(':', 1)
                if len(parts) != 2:
                    continue

                
                self._log_action(action="emotion_analysis_debug", metadata={"line":line}, level=logging.DEBUG)

                # Ensure key is a string before calling lower()
                key = str(parts[0]).strip().lower()  # Explicitly convert to string
                value = str(parts[1]).strip()
                
                self._log_action(action="emotion_analysis_debug", metadata={"line":line, "key": key, "value": value}, level=logging.DEBUG)

                if 'primary emotion' in key:
                    analysis['primary_emotion'] = value
                elif 'intensity' in key:
                    # Convert intensity to integer safely
                    try:
                        analysis['intensity'] = int(value.strip('[]'))
                    except ValueError:
                        analysis['intensity'] = 5  # default value
                elif 'secondary emotions' in key:
                    analysis['secondary_emotions'] = [
                        s.strip() for s in value.split(',') if s.strip()
                    ]
                elif 'emotional triggers' in key:
                    analysis['emotional_triggers'] = [
                        t.strip() for t in value.split(',') if t.strip()
                    ]
                elif 'suggested coping strategies' in key:
                    analysis['coping_strategies'] = [
                        c.strip() for c in value.split(',') if c.strip()
                    ]
                elif 'confidence score' in key:
                    # Convert confidence score to float safely
                    try:
                        analysis['confidence_score'] = float(value.strip('[]'))
                    except ValueError:
                        analysis['confidence_score'] = 0.5
                    
            if not analysis['primary_emotion']:
                raise ValueError("Primary emotion not found in response")
            
            self._log_action(action="emotion_analysis_success", metadata={"response": response, "analysis": analysis}, level=logging.INFO)
            return analysis
                
        except Exception as e:
            self._log_action(
                action="emotion_analysis_error", 
                metadata={"response": str(response), "error": str(e)},
                level=logging.ERROR
            )
            raise ValueError(f"Failed to parse emotion response: {str(e)}")