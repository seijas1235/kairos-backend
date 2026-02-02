"""
Lesson Generator Agent - Generates complete lesson content using Gemini 1.5 Pro.

This agent creates personalized lessons on any topic based on:
- Topic (what to learn)
- Level (beginner/intermediate/advanced)
- Learning style (visual/textual/interactive/mixed)
- Age (for age-appropriate content)

NEW: Generates dynamic curriculum with 6 topics in conversational format
"""
import json
import os
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


class LessonGeneratorAgent:
    """
    Agent responsible for generating complete lesson content using Gemini 1.5 Pro.
    Creates structured, personalized lessons with dynamic curriculum.
    """
    
    def __init__(self):
        self.model_name = "gemini-3-flash-preview"  # GEMINI 3 FLASH
        self.generation_config = {
            "temperature": 0.3,  # Low temperature for following instructions
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,  # Allow longer responses
        }
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized LessonGeneratorAgent with {self.model_name}")
    
    def generate_lesson(
        self,
        topic: str,
        level: str = "beginner",
        learning_style: str = "mixed",
        age: int = None,
        alias: str = None,
        language: str = "en",
        excluded_topics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete lesson with dynamic curriculum.
        
        Args:
            topic: The subject to teach
            level: beginner, intermediate, or advanced
            learning_style: visual, textual, interactive, or mixed
            age: Optional age for age-appropriate content
            alias: Optional student name/alias for personalization
            language: Language code (en, es, pt) for lesson content
            excluded_topics: List of topic titles to exclude (avoid repetition)
            
        Returns:
            Dictionary with lesson structure including curriculum with 6 topics
        """
        prompt = self._build_lesson_prompt(topic, level, learning_style, age, alias, language, excluded_topics)
        
        try:
            self.logger.info(f"Generating lesson with Gemini 3 Flash (temp={self.generation_config['temperature']})")
            response = self.model.generate_content(prompt)
            lesson_data = self._parse_lesson_response(response.text)
            
            # Add metadata
            lesson_data['metadata'] = {
                'topic': topic,
                'level': level,
                'learning_style': learning_style,
                'age': age,
                'generated_by': 'gemini-3-flash',
                'curriculum_version': '2.0'
            }
            
            return lesson_data
            
        except Exception as e:
            self.logger.error(f"Error generating lesson: {str(e)}")
            return self._get_fallback_lesson(topic, level)
    
    def _build_lesson_prompt(
        self,
        topic: str,
        level: str,
        learning_style: str,
        age: int,
        alias: str,
        language: str = "en",
        excluded_topics: List[str] = None
    ) -> str:
        """Build the prompt for lesson generation with dynamic curriculum."""
        
        age_context = f" for a {age}-year-old student" if age else ""
        student_name = alias if alias else "the student"
        greeting = f"Hello {alias}! " if alias else ""
        
        excluded_context = ""
        if excluded_topics:
            excluded_context = f"\n**IMPORTANT - Avoid These Topics:**\nThe student has already learned about: {', '.join(excluded_topics)}\nDo NOT include these topics in the curriculum.\n"
        
        # Language instruction
        language_names = {'en': 'English', 'es': 'Spanish', 'pt': 'Portuguese'}
        language_name = language_names.get(language, 'English')
        language_instruction = f"\n**CRITICAL - Language Requirement:**\nYou MUST generate ALL lesson content in {language_name}. Every message, title, description, and objective must be written in {language_name}.\n"
        
        # Learning style instruction
        learning_style_instructions = {
            'visual': "\n**CRITICAL - Visual Learning Style:**\nThe student learns best through VISUAL content. In EVERY AI message:\n- Describe diagrams, charts, graphs, and visual representations\n- Use visual metaphors and analogies (e.g., 'imagine a picture of...', 'visualize this as...')\n- Suggest mental images and visual patterns\n- Include references to colors, shapes, and spatial relationships\n- Recommend visual resources (videos, infographics, animations)\n",
            'textual': "\n**CRITICAL - Textual Learning Style:**\nThe student learns best through DETAILED TEXT. In EVERY AI message:\n- Provide comprehensive written explanations with rich vocabulary\n- Use precise definitions and terminology\n- Include detailed step-by-step written descriptions\n- Focus on logical written arguments and text-based reasoning\n- Provide reading recommendations and written examples\n",
            'interactive': "\n**CRITICAL - Interactive Learning Style:**\nThe student learns best through HANDS-ON INTERACTION. In EVERY AI message:\n- Include thought experiments and 'what if' scenarios\n- Pose interactive questions that require active thinking\n- Suggest hands-on activities and experiments\n- Use analogies to everyday interactive experiences\n- Encourage mental simulation and active problem-solving\n",
            'mixed': "\n**CRITICAL - Mixed Learning Style:**\nThe student learns best through a COMBINATION of approaches. In EVERY AI message:\n- Combine visual descriptions with detailed text explanations\n- Include both diagrams/charts descriptions AND written analysis\n- Mix interactive questions with comprehensive explanations\n- Use multiple modalities: visual metaphors, detailed text, and thought experiments\n"
        }
        learning_style_instruction = learning_style_instructions.get(learning_style, learning_style_instructions['mixed'])
        
        prompt = f"""You are an expert educator creating a personalized, interactive lesson{age_context}.

**Student Information:**
- Name: {student_name}
- Topic: {topic}
- Level: {level}
- Learning Style: {learning_style}
{excluded_context}{language_instruction}{learning_style_instruction}
**IMPORTANT - Create a Dynamic Curriculum:**
Instead of fixed content blocks, create a conversational learning experience with 6 topics.
Each topic should have multiple messages that guide the student through the material.

**Generate a lesson with:**

1. **Title**: Catchy and descriptive
2. **Description**: 2-3 sentences about what {student_name} will learn
3. **Learning Objectives**: 3-5 specific, measurable objectives
4. **Curriculum**: A structured learning path with 6 topics

**Curriculum Structure:**
Each topic should have:
- **id**: Unique identifier (topic_1, topic_2, etc.)
- **title**: Clear, engaging topic title
- **order**: Sequential number (1-6)
- **messages**: Array of 3-5 conversational messages

**Message Types:**
- **ai**: Content delivered by the AI tutor (most messages)
- **question**: Interactive question for the student
- **encouragement**: Motivational message

**Message Structure:**
Each message should have:
- **type**: "ai", "question", or "encouragement"
- **content**: The actual message text (address {student_name} by name)
- **requires_response**: true if waiting for student to click "continue"

**Personalization Guidelines:**
- Address {student_name} directly in messages
- Use conversational, friendly tone
- Build concepts progressively across topics
- Include real-world examples
- Add encouraging messages between topics

**CRITICAL CONTENT REQUIREMENTS:**
1. **NO PLACEHOLDERS**: Never write "Let me explain the basics" without actually explaining
2. **BE SPECIFIC**: Include actual facts, definitions, formulas, examples
3. **BE THOROUGH**: Each AI message should be 3-5 paragraphs of REAL educational content
4. **TEACH REAL CONCEPTS**: Provide actual information, not motivational fluff
5. **USE EXAMPLES**: Give concrete, real-world examples and analogies

**BAD Example (DO NOT DO THIS):**
"Quantum Physics is a fascinating subject. Let me explain the basics."

**GOOD Example (DO THIS):**
"Quantum Physics is the branch of physics that studies matter and energy at atomic scales. Unlike classical physics, quantum mechanics reveals that particles can exist in multiple states simultaneously—a phenomenon called superposition. For example, an electron doesn't orbit the nucleus like a planet; instead, it exists in a 'cloud of probability.' This was demonstrated in the double-slit experiment, where particles behaved as both waves and particles. This wave-particle duality forms the foundation of modern technology like transistors and lasers."

**Example Topic:**
{{
  "id": "topic_1",
  "title": "Introduction to {topic}",
  "order": 1,
  "messages": [
    {{
      "type": "ai",
      "content": "{greeting}Welcome to our exploration of {topic}! {student_name}, I'm thrilled to guide you through this fascinating subject. {topic} is a fundamental area of study that has revolutionized our understanding of the world. In this lesson, we'll break down complex concepts into digestible pieces, use real-world examples you can relate to, and build your knowledge step by step. By the end, you'll have a solid grasp of the core principles and be able to explain them to others. Let's dive in with curiosity and enthusiasm!",
      "requires_response": true
    }},
    {{
      "type": "ai",
      "content": "Let me start by explaining what {topic} actually is, {student_name}. [INSERT 3-5 PARAGRAPHS OF REAL EDUCATIONAL CONTENT HERE - Include: definition, historical context, key principles, real-world applications, and concrete examples. For instance, if teaching Quantum Physics, explain wave-particle duality with the double-slit experiment, describe superposition with Schrödinger's cat, mention practical applications like quantum computers and MRI machines, and use analogies like 'imagine if you could be in two places at once']",
      "requires_response": true
    }},
    {{
      "type": "question",
      "content": "Now that you understand the basics, {student_name}, can you think of a situation in your daily life where you might encounter {topic} or its applications? Take a moment to reflect on this.",
      "requires_response": true
    }}
  ]
}}

**Return ONLY valid JSON in this exact format:**
```json
{{
  "title": "Lesson title here",
  "description": "Brief description of what will be learned",
  "objectives": [
    "Objective 1",
    "Objective 2",
    "Objective 3"
  ],
  "curriculum": {{
    "total_topics": 6,
    "topics": [
      {{
        "id": "topic_1",
        "title": "Topic 1 title",
        "order": 1,
        "messages": [
          {{
            "type": "ai",
            "content": "Message content with {student_name}...",
            "requires_response": true
          }}
        ]
      }},
      {{
        "id": "topic_2",
        "title": "Topic 2 title",
        "order": 2,
        "messages": [...]
      }}
      // ... 4 more topics (total 6)
    ]
  }},
  "estimated_duration_minutes": 30,
  "difficulty_level": "{level}"
}}
```

**Important:**
- Create exactly 6 topics
- Each topic should have 2-3 messages (NOT 5 short ones)
- Use {level}-appropriate language
- Make it conversational and engaging
- Address {student_name} throughout
- Return ONLY the JSON, no markdown formatting

**CRITICAL FINAL REMINDER:**
Each AI message MUST contain REAL educational content (3-5 paragraphs minimum).
DO NOT write generic statements like "Let me explain" or "This is fascinating" without ACTUALLY explaining.
Include SPECIFIC facts, definitions, examples, and real-world applications in EVERY AI message.
Quality of educational content is MORE IMPORTANT than following the exact JSON structure.
"""
        
        return prompt
    
    def _parse_lesson_response(self, response: str) -> Dict[str, Any]:
        """Parse the Gemini response into structured lesson data."""
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            response = response.strip()
            
            # Parse JSON
            lesson_data = json.loads(response)
            
            # Validate required fields for new curriculum format
            required_fields = ['title', 'description', 'objectives', 'curriculum']
            for field in required_fields:
                if field not in lesson_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate curriculum structure
            if 'topics' not in lesson_data['curriculum']:
                raise ValueError("Curriculum must have 'topics' array")
            
            # Ensure topics have IDs and messages
            for i, topic in enumerate(lesson_data['curriculum']['topics']):
                if 'id' not in topic:
                    topic['id'] = f"topic_{i+1}"
                if 'messages' not in topic:
                    topic['messages'] = []
            
            return lesson_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            self.logger.error(f"Response was: {response[:200]}...")
            raise ValueError("Invalid JSON response from Gemini")
        except Exception as e:
            self.logger.error(f"Error parsing lesson response: {str(e)}")
            raise
    
    def _get_fallback_lesson(self, topic: str, level: str) -> Dict[str, Any]:
        """Return a basic fallback lesson with curriculum structure."""
        return {
            "title": f"Introduction to {topic}",
            "description": f"Learn the basics of {topic} at the {level} level through an interactive conversation.",
            "objectives": [
                f"Understand what {topic} is",
                f"Learn key concepts in {topic}",
                f"Apply {topic} knowledge"
            ],
            "curriculum": {
                "total_topics": 3,
                "topics": [
                    {
                        "id": "topic_1",
                        "title": f"What is {topic}?",
                        "order": 1,
                        "messages": [
                            {
                                "type": "ai",
                                "content": f"Welcome! Let's explore {topic} together.",
                                "requires_response": True
                            },
                            {
                                "type": "ai",
                                "content": f"{topic} is a fascinating subject. Let me explain the basics.",
                                "requires_response": True
                            }
                        ]
                    },
                    {
                        "id": "topic_2",
                        "title": "Key Concepts",
                        "order": 2,
                        "messages": [
                            {
                                "type": "ai",
                                "content": "Now that you understand the basics, let's dive deeper.",
                                "requires_response": True
                            }
                        ]
                    },
                    {
                        "id": "topic_3",
                        "title": "Summary",
                        "order": 3,
                        "messages": [
                            {
                                "type": "ai",
                                "content": "Great job! You've learned the fundamentals.",
                                "requires_response": True
                            }
                        ]
                    }
                ]
            },
            "estimated_duration_minutes": 20,
            "difficulty_level": level,
            "metadata": {
                'topic': topic,
                'level': level,
                'generated_by': 'fallback',
                'note': 'This is a fallback lesson due to generation error'
            }
        }
    
    def generate_additional_topics(
        self,
        original_lesson: Dict[str, Any],
        num_topics: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Generate additional topics to continue the lesson.
        
        Args:
            original_lesson: The original lesson data
            num_topics: Number of new topics to generate (default 6)
            
        Returns:
            List of new topic dictionaries
        """
        topic = original_lesson['metadata']['topic']
        level = original_lesson['metadata']['level']
        alias = original_lesson.get('metadata', {}).get('alias', 'the student')
        
        # Get existing topic titles to avoid repetition
        existing_topics = [t['title'] for t in original_lesson['curriculum']['topics']]
        
        prompt = f"""Continue the lesson on {topic} for {alias}.

**Previous Topics Covered:**
{', '.join(existing_topics)}

**Generate {num_topics} NEW topics** that build upon what was already learned.
Make them progressively more advanced and interesting.

Return ONLY valid JSON array of topics in this format:
```json
[
  {{
    "id": "topic_7",
    "title": "New topic title",
    "order": 7,
    "messages": [
      {{
        "type": "ai",
        "content": "Message content...",
        "requires_response": true
      }}
    ]
  }}
]
```
"""
        
        try:
            response = self.model.generate_content(prompt)
            new_topics = self._parse_topics_response(response.text)
            return new_topics
        except Exception as e:
            self.logger.error(f"Error generating additional topics: {str(e)}")
            return []
    
    def _parse_topics_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse topics array from Gemini response."""
        try:
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            response = response.strip()
            topics = json.loads(response)
            
            if not isinstance(topics, list):
                raise ValueError("Response must be an array of topics")
            
            return topics
        except Exception as e:
            self.logger.error(f"Error parsing topics response: {str(e)}")
            raise
    
    def adapt_message(
        self,
        message: Dict[str, Any],
        emotion: str,
        student_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapt a specific message based on student emotion.
        
        Args:
            message: The message to adapt
            emotion: Current student emotion (engaged, confused, bored, etc.)
            student_context: Additional context about the student
            
        Returns:
            Adapted message
        """
        prompt = f"""Adapt this lesson message based on the student's current emotion.

**Original Message:**
{message.get('content', '')}

**Student State:**
Emotion: {emotion}
Context: {json.dumps(student_context, indent=2)}

**Adaptation Guidelines:**
- If confused: Simplify language, add more examples, break into smaller steps
- If bored: Add interesting facts, real-world connections, make it more engaging
- If frustrated: Provide encouragement, offer alternative explanations
- If engaged: Maintain pace, add depth, introduce advanced concepts

**Return ONLY valid JSON:**
```json
{{
  "content": "Adapted message content...",
  "adaptation_reason": "Why this adaptation was made"
}}
```
"""
        
        try:
            response = self.model.generate_content(prompt)
            adapted = self._parse_adaptation_response(response.text)
            
            # Merge with original message
            adapted_message = message.copy()
            adapted_message['content'] = adapted['content']
            adapted_message['adapted'] = True
            adapted_message['adaptation_reason'] = adapted.get('adaptation_reason', '')
            adapted_message['original_content'] = message.get('content')
            
            return adapted_message
            
        except Exception as e:
            self.logger.error(f"Error adapting message: {str(e)}")
            return message  # Return original if adaptation fails
    
    def _parse_adaptation_response(self, response: str) -> Dict[str, Any]:
        """Parse adaptation response from Gemini."""
        try:
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            response = response.strip()
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error parsing adaptation response: {str(e)}")
            raise
