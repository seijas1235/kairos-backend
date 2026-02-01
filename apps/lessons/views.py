"""
Views for dynamic lesson generation.
"""
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.agents.lesson_generator_agent import LessonGeneratorAgent

logger = logging.getLogger(__name__)


@api_view(['POST'])
def generate_lesson(request):
    """
    Generate a personalized lesson based on user input.
    
    POST /api/v1/lessons/generate/
    
    Request body:
    {
        "topic": "Quantum Physics",
        "level": "beginner",  // beginner, intermediate, advanced
        "learning_style": "visual",  // visual, textual, interactive, mixed
        "age": 14  // optional
    }
    
    Response:
    {
        "lesson_id": "generated_12345",
        "title": "Introduction to Quantum Physics",
        "description": "...",
        "objectives": ["...", "..."],
        "content_blocks": [...],
        "estimated_duration_minutes": 30,
        "difficulty_level": "beginner",
        "metadata": {...}
    }
    """
    try:
        # Extract parameters
        topic = request.data.get('topic')
        level = request.data.get('level', 'beginner')
        learning_style = request.data.get('learning_style', 'mixed')
        age = request.data.get('age')
        
        # Validate required fields
        if not topic:
            return Response(
                {'error': 'Topic is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate level
        valid_levels = ['beginner', 'intermediate', 'advanced']
        if level not in valid_levels:
            return Response(
                {'error': f'Level must be one of: {", ".join(valid_levels)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate learning style
        valid_styles = ['visual', 'textual', 'interactive', 'mixed']
        if learning_style not in valid_styles:
            return Response(
                {'error': f'Learning style must be one of: {", ".join(valid_styles)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Generating lesson: topic={topic}, level={level}, style={learning_style}, age={age}")
        
        # Generate lesson using LessonGeneratorAgent
        agent = LessonGeneratorAgent()
        lesson_data = agent.generate_lesson(
            topic=topic,
            level=level,
            learning_style=learning_style,
            age=age
        )
        
        # Add lesson ID
        import time
        lesson_data['lesson_id'] = f"generated_{int(time.time() * 1000)}"
        
        logger.info(f"Lesson generated successfully: {lesson_data['lesson_id']}")
        
        return Response(lesson_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error generating lesson: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to generate lesson', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def adapt_content(request):
    """
    Adapt a content block based on student emotion.
    
    POST /api/v1/lessons/adapt/
    
    Request body:
    {
        "block": {...},  // Content block to adapt
        "emotion": "confused",
        "student_context": {...}
    }
    """
    try:
        block = request.data.get('block')
        emotion = request.data.get('emotion')
        student_context = request.data.get('student_context', {})
        
        if not block or not emotion:
            return Response(
                {'error': 'Block and emotion are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Adapting content block for emotion: {emotion}")
        
        # Adapt content using LessonGeneratorAgent
        agent = LessonGeneratorAgent()
        adapted_block = agent.adapt_content_block(block, emotion, student_context)
        
        return Response(adapted_block, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error adapting content: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to adapt content', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
