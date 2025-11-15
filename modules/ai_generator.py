"""
AI Generator Module
Handles all AI-powered content generation including notes, quizzes,
flashcards, lesson plans, and doubt solving.
"""

import os
import json
from openai import OpenAI

class AIGenerator:
    """Main class for generating AI-powered educational content"""
    
    def __init__(self):
        """Initialize AI generator with API key"""
        # Get API key from environment or use a default (for demo)
        api_key = os.environ.get('OPENAI_API_KEY', '')
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            print("Warning: OpenAI API key not found. Using mock responses.")
    
    def _call_ai(self, prompt, max_tokens=2000):
        """
        Call OpenAI API or return mock response
        This is a helper method to handle AI calls
        """
        if not self.client:
            # Return mock response for demo purposes
            return self._get_mock_response(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI API Error: {e}")
            return self._get_mock_response(prompt)
    
    def _get_mock_response(self, prompt):
        """Generate mock responses when API is not available"""
        # This provides demo functionality without API key
        if "quiz" in prompt.lower():
            return json.dumps({
                "questions": [
                    {
                        "question": "What is the main topic?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct": 0,
                        "explanation": "This is a sample explanation."
                    }
                ]
            })
        elif "flashcard" in prompt.lower():
            return json.dumps({
                "cards": [
                    {"front": "Question?", "back": "Answer"}
                ]
            })
        else:
            return "This is a sample generated content. Please configure OpenAI API key for full functionality."
    
    def generate(self, topic, content_type='notes', difficulty='medium', language='en'):
        """
        Generate content based on type
        content_type can be: notes, summary, diagram_description, video_script
        """
        # Build prompt based on content type
        prompts = {
            'notes': f"Create comprehensive study notes on '{topic}' suitable for {difficulty} level students. Include key concepts, definitions, examples, and important points.",
            'summary': f"Create a concise summary of '{topic}' for {difficulty} level. Include main points and key takeaways.",
            'diagram_description': f"Describe a visual diagram or concept map for '{topic}' suitable for {difficulty} level. Include what elements should be shown and how they connect.",
            'video_script': f"Create an engaging video script for teaching '{topic}' to {difficulty} level students. Include introduction, main content, examples, and conclusion."
        }
        
        prompt = prompts.get(content_type, prompts['notes'])
        
        # Add language instruction if not English
        if language != 'en':
            prompt += f" Translate the content to {language}."
        
        result = self._call_ai(prompt)
        
        # Format result based on content type
        if content_type == 'notes':
            return {
                'type': 'notes',
                'topic': topic,
                'content': result,
                'difficulty': difficulty
            }
        elif content_type == 'summary':
            return {
                'type': 'summary',
                'topic': topic,
                'content': result,
                'difficulty': difficulty
            }
        elif content_type == 'diagram_description':
            return {
                'type': 'diagram',
                'topic': topic,
                'description': result,
                'difficulty': difficulty
            }
        elif content_type == 'video_script':
            return {
                'type': 'video_script',
                'topic': topic,
                'script': result,
                'difficulty': difficulty
            }
        
        return {'type': content_type, 'content': result}
    
    def generate_quiz(self, topic, num_questions=10, difficulty='medium'):
        """Generate quiz with multiple choice questions"""
        prompt = f"""Create {num_questions} multiple-choice questions on '{topic}' for {difficulty} level students.
        Format as JSON with this structure:
        {{
            "questions": [
                {{
                    "question": "Question text",
                    "options": ["A", "B", "C", "D"],
                    "correct": 0,
                    "explanation": "Why this answer is correct"
                }}
            ]
        }}"""
        
        result = self._call_ai(prompt, max_tokens=3000)
        
        # Try to parse JSON, fallback to structured format
        try:
            return json.loads(result)
        except:
            return {
                'questions': [
                    {
                        'question': f"Sample question about {topic}?",
                        'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                        'correct': 0,
                        'explanation': 'Sample explanation'
                    }
                ]
            }
    
    def generate_flashcards(self, topic, num_cards=20):
        """Generate flashcards for a topic"""
        prompt = f"""Create {num_cards} flashcards on '{topic}'.
        Format as JSON:
        {{
            "cards": [
                {{"front": "Question or term", "back": "Answer or definition"}}
            ]
        }}"""
        
        result = self._call_ai(prompt, max_tokens=2000)
        
        try:
            return json.loads(result)
        except:
            return {
                'cards': [
                    {'front': f'What is {topic}?', 'back': f'Definition of {topic}'}
                ]
            }
    
    def solve_doubt(self, question, context=''):
        """Solve student doubts using AI"""
        prompt = f"""A student asks: "{question}"
        {f"Context: {context}" if context else ""}
        
        Provide a clear, educational explanation that helps the student understand.
        Use simple language and include examples if helpful."""
        
        answer = self._call_ai(prompt)
        return {
            'question': question,
            'answer': answer,
            'context': context
        }
    
    def generate_lesson_plan(self, topic, duration=60, grade_level='middle'):
        """Generate lesson plan for teachers"""
        prompt = f"""Create a detailed lesson plan for teaching '{topic}' to {grade_level} level students.
        Duration: {duration} minutes.
        
        Include:
        - Learning objectives
        - Materials needed
        - Step-by-step activities
        - Assessment methods
        - Homework suggestions"""
        
        result = self._call_ai(prompt, max_tokens=2500)
        
        return {
            'topic': topic,
            'duration': duration,
            'grade_level': grade_level,
            'plan': result
        }
    
    def generate_homework(self, topic, difficulty='medium'):
        """Generate homework assignments"""
        prompt = f"""Create homework assignments on '{topic}' for {difficulty} level students.
        Include:
        - Clear instructions
        - Multiple question types (short answer, essay, problems)
        - Expected completion time
        - Answer key for teachers"""
        
        result = self._call_ai(prompt, max_tokens=2000)
        
        return {
            'topic': topic,
            'difficulty': difficulty,
            'homework': result
        }

