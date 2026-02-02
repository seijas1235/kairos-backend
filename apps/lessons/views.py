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
        learning_style = request.data.get('learningStyle', 'mixed')  # camelCase from frontend
        age = request.data.get('age')
        alias = request.data.get('alias')  # Student name/alias
        language = request.data.get('language', 'en')  # Default to English
        excluded_topics = request.data.get('excluded_topics', [])  # Topics to avoid
        
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
        
        logger.info(f"Generating lesson: topic={topic}, level={level}, style={learning_style}, age={age}, alias={alias}, language={language}, excluded={len(excluded_topics)}")
        
        # Generate lesson using AI Orchestrator (manages Gemini 3 models)
        from apps.agents.orchestrator import AIOrchestrator
        orchestrator = AIOrchestrator()
        lesson_data = orchestrator.generate_lesson(
            topic=topic,
            level=level,
            learning_style=learning_style,
            age=age,
            alias=alias,
            language=language,
            excluded_topics=excluded_topics
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


@api_view(['POST'])
def continue_lesson(request):
    """
    Generate additional topics to continue a lesson.
    
    POST /api/v1/lessons/continue/
    
    Request body:
    {
        "lesson": {...},  // Original lesson data
        "num_topics": 6  // Number of new topics to generate (default 6)
    }
    
    Response:
    {
        "topics": [...]  // Array of new topic objects
    }
    """
    try:
        lesson = request.data.get('lesson')
        num_topics = request.data.get('num_topics', 6)
        
        if not lesson:
            return Response(
                {'error': 'Lesson data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(num_topics, int) or num_topics < 1 or num_topics > 10:
            return Response(
                {'error': 'num_topics must be an integer between 1 and 10'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Generating {num_topics} additional topics for lesson")
        
        # Generate additional topics using LessonGeneratorAgent
        agent = LessonGeneratorAgent()
        new_topics = agent.generate_additional_topics(lesson, num_topics)
        
        return Response({'topics': new_topics}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating additional topics: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to generate additional topics', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def adapt_message(request):
    """
    Adapt a specific message based on student emotion.
    
    POST /api/v1/lessons/adapt-message/
    
    Request body:
    {
        "message": {...},  // Message to adapt
        "emotion": "confused",
        "student_context": {...}
    }
    """
    try:
        message = request.data.get('message')
        emotion = request.data.get('emotion')
        student_context = request.data.get('student_context', {})
        
        if not message or not emotion:
            return Response(
                {'error': 'Message and emotion are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Adapting message for emotion: {emotion}")
        
        # Adapt message using LessonGeneratorAgent
        agent = LessonGeneratorAgent()
        adapted_message = agent.adapt_message(message, emotion, student_context)
        
        return Response(adapted_message, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error adapting message: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to adapt message', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
