"""
Study Material Fetcher Module
Fetches study material from internet sources like Wikipedia, DuckDuckGo search,
and other educational websites. Compiles information to create comprehensive study materials.
"""

import requests
import json
import html
import re
from typing import Dict, List, Optional
from urllib.parse import quote

class StudyMaterialFetcher:
    """Fetches study material from internet sources"""
    
    def __init__(self, ai_generator=None):
        """
        Initialize study material fetcher
        ai_generator: Optional AIGenerator instance for compiling and enhancing content
        """
        self.ai_generator = ai_generator
        # Wikipedia API endpoint
        self.wikipedia_api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        # Wikipedia search API
        self.wikipedia_search_url = "https://en.wikipedia.org/api/rest_v1/page/search/"
        # DuckDuckGo instant answer API (no API key needed)
        self.duckduckgo_ia_url = "https://api.duckduckgo.com/"
    
    def _clean_html(self, text: str) -> str:
        """
        Remove HTML tags and decode HTML entities
        """
        if not text:
            return ""
        # Decode HTML entities
        text = html.unescape(text)
        # Remove basic HTML tags (simple approach)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
    
    def fetch_from_wikipedia(self, topic: str) -> Optional[Dict]:
        """
        Fetch information from Wikipedia API
        Returns summary and extract from Wikipedia page
        """
        try:
            # URL encode the topic
            encoded_topic = quote(topic)
            
            # Try to get page summary
            url = f"{self.wikipedia_api_url}{encoded_topic}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information
                result = {
                    'title': data.get('title', topic),
                    'extract': self._clean_html(data.get('extract', '')),
                    'description': self._clean_html(data.get('description', '')),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'source': 'Wikipedia'
                }
                
                # If extract is too short, try to get full page content
                if len(result['extract']) < 200:
                    # Try search API to find better match
                    search_url = f"{self.wikipedia_search_url}?q={encoded_topic}&limit=1"
                    search_response = requests.get(search_url, timeout=10)
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        if search_data.get('pages'):
                            page = search_data['pages'][0]
                            result['extract'] = self._clean_html(page.get('snippet', result['extract']))
                            result['title'] = page.get('title', result['title'])
                
                return result if result.get('extract') else None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Wikipedia: {e}")
            return None
        except Exception as e:
            print(f"Error processing Wikipedia response: {e}")
            return None
    
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search DuckDuckGo for relevant information
        Returns list of search results with snippets
        """
        try:
            # DuckDuckGo HTML search (no official API, but we can use their instant answer)
            # For more comprehensive search, we'll use a simple approach
            # Note: DuckDuckGo doesn't have a public search API, so we'll use Wikipedia as primary source
            # and supplement with other free sources if needed
            
            # For now, return empty list - we can enhance this later with web scraping
            # if needed, but Wikipedia should provide good coverage
            return []
            
        except Exception as e:
            print(f"Error searching DuckDuckGo: {e}")
            return []
    
    def fetch_educational_content(self, topic: str) -> Dict:
        """
        Fetch educational content from multiple internet sources
        Combines information from Wikipedia and other sources
        """
        all_content = []
        
        # Fetch from Wikipedia (primary source)
        wikipedia_data = self.fetch_from_wikipedia(topic)
        if wikipedia_data:
            all_content.append(wikipedia_data)
        
        # Try alternative search terms if Wikipedia didn't return good results
        if not wikipedia_data or len(wikipedia_data.get('extract', '')) < 100:
            # Try with "explanation" or "definition" appended
            alternative_queries = [
                f"{topic} explanation",
                f"{topic} definition",
                f"what is {topic}"
            ]
            
            for alt_query in alternative_queries:
                alt_data = self.fetch_from_wikipedia(alt_query)
                if alt_data and len(alt_data.get('extract', '')) > 100:
                    all_content.append(alt_data)
                    break
        
        return {
            'topic': topic,
            'sources': all_content,
            'total_sources': len(all_content)
        }
    
    def compile_study_material(self, topic: str, content_type: str = 'notes', 
                              difficulty: str = 'medium', language: str = 'en') -> Dict:
        """
        Fetch information from internet and compile into study material
        Uses AI generator to organize and enhance the fetched content
        """
        # Fetch content from internet
        internet_content = self.fetch_educational_content(topic)
        
        # If we have internet content, use AI to compile it
        if internet_content.get('sources') and self.ai_generator:
            # Build a comprehensive prompt with internet sources
            sources_text = ""
            for source in internet_content['sources']:
                sources_text += f"\n\nSource: {source.get('title', 'Unknown')} ({source.get('source', 'Unknown')})\n"
                sources_text += f"{source.get('extract', '')}\n"
                if source.get('url'):
                    sources_text += f"Reference: {source.get('url')}\n"
            
            # Create enhanced prompt for AI
            if content_type == 'notes':
                prompt = f"""Based on the following information from internet sources about '{topic}', 
create comprehensive study notes suitable for {difficulty} level students.

Internet Sources Information:
{sources_text}

Please create well-organized study notes that:
1. Synthesize information from the sources above
2. Include key concepts, definitions, and important points
3. Organize content in a clear, structured format
4. Add examples and explanations where helpful
5. Maintain accuracy based on the source material

Format the notes with clear headings and sections."""
            
            elif content_type == 'summary':
                prompt = f"""Based on the following information from internet sources about '{topic}', 
create a concise summary suitable for {difficulty} level.

Internet Sources Information:
{sources_text}

Please create a summary that:
1. Captures the main points from the sources
2. Is clear and easy to understand
3. Includes key takeaways"""
            
            else:
                # For other content types, use standard prompt but include internet sources
                prompt = f"""Create {content_type} on '{topic}' for {difficulty} level students.

Additional information from internet sources:
{sources_text}

Use this information to create accurate and comprehensive content."""
            
            # Add language instruction if not English
            if language != 'en':
                prompt += f"\n\nTranslate the content to {language}."
            
            # Generate content using AI with internet sources
            if hasattr(self.ai_generator, '_call_ai'):
                ai_result = self.ai_generator._call_ai(prompt, max_tokens=3000)
            else:
                # Fallback if _call_ai is not available
                ai_result = self.ai_generator.generate(
                    topic=topic,
                    content_type=content_type,
                    difficulty=difficulty,
                    language=language
                )
                if isinstance(ai_result, dict):
                    ai_result = ai_result.get('content', str(ai_result))
            
            # Format result
            if content_type == 'notes':
                return {
                    'type': 'notes',
                    'topic': topic,
                    'content': ai_result,
                    'difficulty': difficulty,
                    'sources': [s.get('url') for s in internet_content.get('sources', []) if s.get('url')],
                    'generated_from_internet': True
                }
            elif content_type == 'summary':
                return {
                    'type': 'summary',
                    'topic': topic,
                    'content': ai_result,
                    'difficulty': difficulty,
                    'sources': [s.get('url') for s in internet_content.get('sources', []) if s.get('url')],
                    'generated_from_internet': True
                }
            else:
                return {
                    'type': content_type,
                    'topic': topic,
                    'content': ai_result,
                    'difficulty': difficulty,
                    'sources': [s.get('url') for s in internet_content.get('sources', []) if s.get('url')],
                    'generated_from_internet': True
                }
        
        # Fallback to AI generation without internet sources if fetching failed
        if self.ai_generator:
            print(f"Internet fetch failed, falling back to AI generation for: {topic}")
            return self.ai_generator.generate(
                topic=topic,
                content_type=content_type,
                difficulty=difficulty,
                language=language
            )
        
        # Last resort: return basic structure
        return {
            'type': content_type,
            'topic': topic,
            'content': f"Study material about {topic} (internet sources unavailable)",
            'difficulty': difficulty,
            'generated_from_internet': False
        }

