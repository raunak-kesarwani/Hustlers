"""
AI Generator Module
Handles all AI-powered content generation including notes, quizzes,
flashcards, lesson plans, and doubt solving.
Uses Google Gemini API for AI functionality.
"""

import os
import json
import google.generativeai as genai

class AIGenerator:
    """Main class for generating AI-powered educational content"""
    
    def __init__(self):
        """Initialize AI generator with Gemini API key"""
        # Get Gemini API key from environment
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            # Configure Gemini API with the provided key
            genai.configure(api_key=api_key)
            # Initialize the model (using gemini-pro for text generation)
            self.model = genai.GenerativeModel('gemini-pro')
            self.api_available = True
        else:
            self.model = None
            self.api_available = False
            print("Warning: Gemini API key not found. Using mock responses.")
    
    def _call_ai(self, prompt, max_tokens=2000):
        """
        Call Gemini API or return mock response
        This is a helper method to handle AI calls
        """
        if not self.api_available or not self.model:
            # Return mock response for demo purposes
            return self._get_mock_response(prompt)
        
        try:
            # Build the full prompt with system instruction
            full_prompt = f"You are an expert educational content creator. {prompt}"
            
            # Generate content using Gemini API
            # Note: Gemini uses max_output_tokens instead of max_tokens
            generation_config = {
                "temperature": 0.7,
                "max_output_tokens": max_tokens,
            }
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Return the generated text
            return response.text
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
            return "This is a sample generated content. Please configure Gemini API key for full functionality."
    
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
        """
        Generate quiz with multiple choice questions related to the given topic
        Creates questions that are directly relevant to the topic provided by the user
        """
        # Enhanced prompt to generate topic-specific quiz questions
        # The topic is emphasized multiple times to ensure questions are strictly related to it
        prompt = f"""You are creating a quiz about the specific topic: "{topic}"

        CRITICAL REQUIREMENT: Every single question MUST be directly and specifically about "{topic}". 
        Do NOT create general knowledge questions. Every question must relate to "{topic}".

        Create exactly {num_questions} multiple-choice questions that are:
        1. Directly about the topic: "{topic}"
        2. Testing knowledge and understanding of "{topic}" specifically
        3. Covering different aspects, concepts, and details of "{topic}"
        4. Appropriate for {difficulty} difficulty level students
        5. Each with exactly 4 answer options (A, B, C, D)
        6. Including clear explanations that reference "{topic}"

        Question Requirements:
        - Each question must mention or clearly relate to "{topic}"
        - Questions should explore: definitions, concepts, processes, facts, applications, or examples related to "{topic}"
        - Options should be plausible but only one should be correct
        - Explanations must explain why the answer is correct in the context of "{topic}"

        Format as JSON with this exact structure:
        {{
            "questions": [
                {{
                    "question": "A specific question about {topic}",
                    "options": ["Option A related to {topic}", "Option B related to {topic}", "Option C related to {topic}", "Option D related to {topic}"],
                    "correct": 0,
                    "explanation": "Explanation that clearly connects the answer to {topic}"
                }}
            ]
        }}
        
        Remember: ALL questions must be about "{topic}" - no generic questions allowed.
        Return ONLY valid JSON, no additional text before or after."""
        
        result = self._call_ai(prompt, max_tokens=4000)
        
        # Try to parse JSON, with better error handling
        try:
            # Clean the result - remove any markdown code blocks if present
            cleaned_result = result.strip()
            if cleaned_result.startswith('```'):
                # Remove markdown code blocks
                lines = cleaned_result.split('\n')
                cleaned_result = '\n'.join(lines[1:-1]) if lines[-1].strip() == '```' else '\n'.join(lines[1:])
            
            # Parse JSON
            quiz_data = json.loads(cleaned_result)
            
            # Validate structure
            if not isinstance(quiz_data, dict) or 'questions' not in quiz_data:
                raise ValueError("Invalid quiz structure")
            
            # Ensure we have questions
            if not quiz_data.get('questions') or len(quiz_data['questions']) == 0:
                raise ValueError("No questions generated")
            
            return quiz_data
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing quiz JSON: {e}")
            print(f"Raw response: {result[:200]}...")  # Print first 200 chars for debugging
            
            # Fallback: return a structured format with a sample question
            return {
                'questions': [
                    {
                        'question': f"What is a key concept related to {topic}?",
                        'options': [
                            f'Option A related to {topic}',
                            f'Option B related to {topic}',
                            f'Option C related to {topic}',
                            f'Option D related to {topic}'
                        ],
                        'correct': 0,
                        'explanation': f'This is a sample question about {topic}. Please check your API configuration for full functionality.'
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

