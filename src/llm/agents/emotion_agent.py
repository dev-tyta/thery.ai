from typing import Dict, Any
from .base_agent import BaseAgent

class EmotionAgent(BaseAgent):
    def process(self, text: str) -> Dict[str, Any]:
        """Process text for emotional content"""
        prompt = self._construct_emotion_prompt(text)
        response = self.llm.generate(prompt)
        
        analysis = self._parse_emotion_response(response.content)
        self._log_action("emotion_analysis", {"text": text, "analysis": analysis})
        
        return analysis
    
    def _construct_emotion_prompt(self, text: str) -> str:
        return f"""
            Analyze the emotional content in the following text:
            Text: {text}
            
            Provide analysis in the following format:
            1. Primary emotion: [single emotion]
            2. Intensity: [number between 1 and 10]
            3. Secondary emotions: [comma-separated list of emotions]
            4. Emotional triggers: [comma-separated list of triggers]
            5. Suggested coping strategies: [comma-separated list of strategies]
            
            Example:
            1. Primary emotion: Anxiety
            2. Intensity: 7
            3. Secondary emotions: Fear, Worry
            4. Emotional triggers: Work deadline, Family conflict
            5. Suggested coping strategies: Deep breathing, Journaling, Talking to a friend
        """
    
    def _parse_emotion_response(self, response: str) -> Dict[str, Any]:
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        analysis = {}
        
        for line in lines:
            if line.startswith('1.'):
                analysis['primary_emotion'] = line.replace('1.', '').strip()
            elif line.startswith('2.'):
                try:
                    intensity = int(line.replace('2.', '').strip().split()[0])
                    analysis['intensity'] = min(max(intensity, 1), 10)
                except ValueError:
                    analysis['intensity'] = 1
            elif line.startswith('3.'):
                secondary = line.replace('3.', '').strip()
                analysis['secondary_emotions'] = [e.strip() for e in secondary.split(',') if e.strip()]
            elif line.startswith('4.'):
                triggers = line.replace('4.', '').strip()
                analysis['triggers'] = [t.strip() for t in triggers.split(',') if t.strip()]
            elif line.startswith('5.'):
                strategies = line.replace('5.', '').strip()
                analysis['coping_strategies'] = [s.strip() for s in strategies.split(',') if s.strip()]
        
        analysis['raw_analysis'] = response
        return analysis