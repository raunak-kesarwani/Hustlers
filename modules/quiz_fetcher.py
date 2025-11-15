"""
Quiz Fetcher Module
Fetches quiz questions from online sources like Open Trivia Database API.
Falls back to AI generation for specific topics not available in public APIs.
"""

import requests
import json
import html
import random
from typing import Dict, List, Optional

class QuizFetcher:
    """Fetches quiz questions from internet sources"""
    
    def __init__(self, ai_generator=None):
        """
        Initialize quiz fetcher
        ai_generator: Optional AIGenerator instance for fallback
        """
        self.ai_generator = ai_generator
        # Open Trivia Database API endpoint
        self.opentdb_base_url = "https://opentdb.com/api.php"
        # Category mapping for common topics
        self.category_map = {
            'science': 17,
            'mathematics': 19,
            'computers': 18,
            'history': 23,
            'geography': 22,
            'sports': 21,
            'animals': 27,
            'mythology': 20,
            'politics': 24,
            'art': 25,
            'celebrities': 26,
            'vehicles': 28,
            'entertainment': None,  # Multiple subcategories
            'general': 9
        }
    
    def _map_topic_to_category(self, topic: str) -> Optional[int]:
        """
        Map a topic string to Open Trivia Database category ID
        Returns category ID or None if no match found
        """
        topic_lower = topic.lower()
        
        # Check for direct matches
        for keyword, category_id in self.category_map.items():
            if keyword in topic_lower and category_id:
                return category_id
        
        # Return general knowledge as default
        return 9
    
    def _map_difficulty(self, difficulty: str) -> str:
        """
        Map our difficulty levels to Open Trivia Database format
        Open Trivia uses: easy, medium, hard
        """
        difficulty_lower = difficulty.lower()
        if difficulty_lower in ['easy', 'medium', 'hard']:
            return difficulty_lower
        # Default to medium
        return 'medium'
    
    def _decode_html_entities(self, text: str) -> str:
        """
        Decode HTML entities in text
        Open Trivia Database returns HTML-encoded text
        """
        return html.unescape(text)
    
    def _format_opentdb_question(self, q: Dict) -> Dict:
        """
        Format Open Trivia Database question to our standard format
        """
        # Decode HTML entities
        question = self._decode_html_entities(q['question'])
        correct_answer = self._decode_html_entities(q['correct_answer'])
        
        # Combine incorrect and correct answers, then shuffle
        all_answers = [self._decode_html_entities(ans) for ans in q['incorrect_answers']]
        all_answers.append(correct_answer)
        
        # Find correct answer index after adding it
        correct_index = len(all_answers) - 1
        
        # Shuffle answers to randomize option order
        # Move correct answer to a random position
        random.shuffle(all_answers)
        # Find new correct index after shuffling
        correct_index = all_answers.index(correct_answer)
        
        return {
            'question': question,
            'options': all_answers,
            'correct': correct_index,
            'explanation': f"The correct answer is {correct_answer}."
        }
    
    def fetch_from_opentdb(self, topic: str, num_questions: int, difficulty: str) -> Optional[Dict]:
        """
        Fetch quiz questions from Open Trivia Database API
        Returns formatted quiz data or None if failed
        """
        try:
            # Map topic to category
            category_id = self._map_topic_to_category(topic)
            mapped_difficulty = self._map_difficulty(difficulty)
            
            # Build API request parameters
            params = {
                'amount': min(num_questions, 50),  # API limit is 50
                'type': 'multiple',  # Multiple choice questions
                'difficulty': mapped_difficulty
            }
            
            # Add category if we found a match
            if category_id:
                params['category'] = category_id
            
            # Make API request
            response = requests.get(self.opentdb_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if request was successful
            if data.get('response_code') == 0 and data.get('results'):
                # Format questions to our standard format
                formatted_questions = [
                    self._format_opentdb_question(q) 
                    for q in data['results']
                ]
                
                return {
                    'questions': formatted_questions
                }
            else:
                # API returned error or no results
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Open Trivia DB: {e}")
            return None
        except Exception as e:
            print(f"Error processing Open Trivia DB response: {e}")
            return None
    
    def fetch_quiz(self, topic: str, num_questions: int = 10, difficulty: str = 'medium') -> Dict:
        """
        Fetch quiz questions from internet sources
        Tries Open Trivia Database first, falls back to AI generation if needed
        
        Args:
            topic: The topic for the quiz
            num_questions: Number of questions to fetch
            difficulty: Difficulty level (easy, medium, hard)
        
        Returns:
            Dictionary with 'questions' key containing list of question dicts
        """
        # Try to fetch from Open Trivia Database
        quiz_data = self.fetch_from_opentdb(topic, num_questions, difficulty)
        
        # If we got enough questions, return them
        if quiz_data and len(quiz_data.get('questions', [])) >= num_questions:
            # Trim to requested number
            quiz_data['questions'] = quiz_data['questions'][:num_questions]
            return quiz_data
        
        # If we got some questions but not enough, use them and supplement with AI
        if quiz_data and len(quiz_data.get('questions', [])) > 0:
            remaining = num_questions - len(quiz_data['questions'])
            if self.ai_generator and remaining > 0:
                # Get additional questions from AI
                ai_quiz = self.ai_generator.generate_quiz(topic, remaining, difficulty)
                if ai_quiz and ai_quiz.get('questions'):
                    quiz_data['questions'].extend(ai_quiz['questions'][:remaining])
            return quiz_data
        
        # Fallback to AI generation if no internet data available
        if self.ai_generator:
            print(f"Falling back to AI generation for topic: {topic}")
            return self.ai_generator.generate_quiz(topic, num_questions, difficulty)
        
        # Last resort: return empty quiz
        return {
            'questions': [
                {
                    'question': f'Sample question about {topic}?',
                    'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                    'correct': 0,
                    'explanation': 'This is a placeholder question. Please configure internet quiz sources or AI generator.'
                }
            ]
        }

