"""
Lesson Generator Agent - Generates complete lesson content using Gemini 3 Pro.

This agent creates personalized lessons on any topic based on:
- Topic (what to learn)
- Level (beginner/intermediate/advanced)
- Learning style (visual/textual/interactive/mixed)
- Age (for age-appropriate content)
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
    Agent responsible for generating complete lesson content using Gemini 3 Pro.
    Creates structured, personalized lessons on any topic.
    """
    
    def __init__(self):
        self.model_name = "gemini-1.5-pro"
        self.model = genai.GenerativeModel(self.model_name)
        self.logger = logging.getLogger(__name__)
        self.temperature = 0.7  # Creative but consistent
    
    def generate_lesson(
        self,
        topic: str,
        level: str = "beginner",
        learning_style: str = "mixed",
        age: int = None
    ) -> Dict[str, Any]:
        """
        Generate a complete lesson on the given topic.
        
        Args:
            topic: The subject to teach
            level: beginner, intermediate, or advanced
            learning_style: visual, textual, interactive, or mixed
            age: Optional age for age-appropriate content
            
        Returns:
            Dictionary with lesson structure including title, description, and content blocks
        """
        prompt = self._build_lesson_prompt(topic, level, learning_style, age)
        
        try:
            response = self.model.generate_content(prompt)
            lesson_data = self._parse_lesson_response(response.text)
            
            # Add metadata
            lesson_data['metadata'] = {
                'topic': topic,
                'level': level,
                'learning_style': learning_style,
                'age': age,
                'generated_by': 'gemini-1.5-pro'
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
        age: int
    ) -> str:
        """Build the prompt for lesson generation."""
        
        age_context = f" for a {age}-year-old student" if age else ""
        
        prompt = f"""You are an expert educator creating a personalized lesson{age_context}.

**Lesson Requirements:**
- Topic: {topic}
- Level: {level}
- Learning Style: {learning_style}
- Make it engaging, clear, and well-structured

**Generate a complete lesson with:**

1. **Title**: Catchy and descriptive
2. **Description**: 2-3 sentences about what the student will learn
3. **Learning Objectives**: 3-5 specific, measurable objectives
4. **Content Blocks**: 5-7 blocks of content

**Content Block Types:**
- **explanation**: Core concepts and theory
- **example**: Real-world examples and applications
- **visual**: Descriptions for visualizations/diagrams
- **practice**: Interactive questions or exercises
- **summary**: Key takeaways

**Learning Style Focus:**
- visual: Include more visual blocks with diagram descriptions
- textual: Focus on clear explanations and written content
- interactive: Include more practice and hands-on blocks
- mixed: Balance all types

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
  "content_blocks": [
    {{
      "id": "block_1",
      "type": "explanation",
      "title": "Block title",
      "content": "Detailed content here...",
      "duration_minutes": 5
    }},
    {{
      "id": "block_2",
      "type": "example",
      "title": "Example title",
      "content": "Example content...",
      "duration_minutes": 3
    }}
  ],
  "estimated_duration_minutes": 30,
  "difficulty_level": "{level}"
}}
```

**Important:**
- Use {level}-appropriate language and complexity
- Make content engaging and interactive
- Include practical applications
- Keep explanations clear and concise
- Return ONLY the JSON, no markdown formatting or extra text
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
            
            # Validate required fields
            required_fields = ['title', 'description', 'objectives', 'content_blocks']
            for field in required_fields:
                if field not in lesson_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure content blocks have IDs
            for i, block in enumerate(lesson_data['content_blocks']):
                if 'id' not in block:
                    block['id'] = f"block_{i+1}"
            
            return lesson_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            self.logger.error(f"Response was: {response[:200]}...")
            raise ValueError("Invalid JSON response from Gemini")
        except Exception as e:
            self.logger.error(f"Error parsing lesson response: {str(e)}")
            raise
    
    def _get_fallback_lesson(self, topic: str, level: str) -> Dict[str, Any]:
        """Return a basic fallback lesson if generation fails."""
        return {
            "title": f"Introduction to {topic}",
            "description": f"Learn the basics of {topic} at the {level} level.",
            "objectives": [
                f"Understand what {topic} is",
                f"Learn key concepts in {topic}",
                f"Apply {topic} knowledge"
            ],
            "content_blocks": [
                {
                    "id": "block_1",
                    "type": "explanation",
                    "title": f"What is {topic}?",
                    "content": f"This lesson will introduce you to {topic}. We'll explore the fundamental concepts and practical applications.",
                    "duration_minutes": 10
                },
                {
                    "id": "block_2",
                    "type": "example",
                    "title": "Real-World Applications",
                    "content": f"{topic} is used in many areas. Let's explore some practical examples.",
                    "duration_minutes": 10
                },
                {
                    "id": "block_3",
                    "type": "practice",
                    "title": "Practice Exercise",
                    "content": "Now it's your turn to apply what you've learned.",
                    "duration_minutes": 10
                }
            ],
            "estimated_duration_minutes": 30,
            "difficulty_level": level,
            "metadata": {
                'topic': topic,
                'level': level,
                'generated_by': 'fallback',
                'note': 'This is a fallback lesson due to generation error'
            }
        }
    
    def adapt_content_block(
        self,
        block: Dict[str, Any],
        emotion: str,
        student_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapt a specific content block based on student emotion.
        
        Args:
            block: The content block to adapt
            emotion: Current student emotion (engaged, confused, bored, etc.)
            student_context: Additional context about the student
            
        Returns:
            Adapted content block
        """
        prompt = f"""Adapt this lesson content based on the student's current state.

**Original Content:**
Title: {block.get('title', '')}
Content: {block.get('content', '')}

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
  "title": "Adapted title",
  "content": "Adapted content...",
  "adaptation_reason": "Why this adaptation was made"
}}
```
"""
        
        try:
            response = self.model.generate_content(prompt)
            adapted = self._parse_lesson_response(response.text)
            
            # Merge with original block
            adapted_block = block.copy()
            adapted_block.update(adapted)
            adapted_block['adapted'] = True
            adapted_block['original_content'] = block.get('content')
            
            return adapted_block
            
        except Exception as e:
            self.logger.error(f"Error adapting content block: {str(e)}")
            return block  # Return original if adaptation fails
