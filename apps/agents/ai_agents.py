"""
KAIROS Multi-Agent System - Gemini 3 Implementation
====================================================

This module exports all 5 specialized AI agents for the KAIROS adaptive learning platform.
Each agent uses either Gemini 3 Flash (for speed) or Gemini 3 Pro (for quality).

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                  Agent Orchestrator                         │
    │              (Coordinates all agents)                       │
    └───┬─────────┬─────────┬─────────┬─────────┬─────────────────┘
        │         │         │         │         │
    ┌───▼───┐ ┌──▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼────┐
    │Emotion│ │Content│ │Learning│ │Assess-│ │Personal│
    │Agent  │ │Adapter│ │Path   │ │ment   │ │ity     │
    │       │ │Agent  │ │Agent  │ │Agent  │ │Agent   │
    │Flash  │ │Pro    │ │Pro    │ │Pro    │ │Flash   │
    └───────┘ └───────┘ └───────┘ └───────┘ └────────┘

Usage:
    from apps.agents.ai_agents import (
        EmotionAgent,
        ContentAdapterAgent,
        LearningPathAgent,
        AssessmentAgent,
        PersonalityAgent
    )
    
    # Initialize agents
    emotion = EmotionAgent()
    content = ContentAdapterAgent()
    
    # Use agents
    result = await emotion.process({'frame': base64_image, 'timestamp': '...'})
"""

from .emotion_agent import EmotionAgent
from .content_adapter_agent import ContentAdapterAgent
from .learning_path_agent import LearningPathAgent
from .assessment_agent import AssessmentAgent
from .personality_agent import PersonalityAgent

__all__ = [
    'EmotionAgent',
    'ContentAdapterAgent',
    'LearningPathAgent',
    'AssessmentAgent',
    'PersonalityAgent',
    'AGENT_MODELS',
    'AGENT_DESCRIPTIONS'
]

# Model assignments for reference
AGENT_MODELS = {
    'EmotionAgent': 'gemini-3.0-flash',      # Fast emotion detection (3-second intervals)
    'ContentAdapterAgent': 'gemini-3.0-pro',  # Intelligent content adaptation
    'LearningPathAgent': 'gemini-3.0-pro',    # Learning path optimization
    'AssessmentAgent': 'gemini-3.0-pro',      # Comprehension evaluation
    'PersonalityAgent': 'gemini-3.0-flash'    # Tone personalization
}

# Agent descriptions for documentation
AGENT_DESCRIPTIONS = {
    'EmotionAgent': {
        'model': 'gemini-3.0-flash',
        'purpose': 'Detects facial emotions in real-time',
        'input': 'Base64 encoded video frames',
        'output': 'Emotion state (engaged|confused|bored|frustrated|neutral)',
        'frequency': 'Every 3 seconds',
        'system_prompt': 'Expert in body language and facial expression analysis'
    },
    'ContentAdapterAgent': {
        'model': 'gemini-3.0-pro',
        'purpose': 'Transforms content based on detected emotions',
        'input': 'Current content + emotion state',
        'output': 'Adapted content with strategy explanation',
        'strategies': ['visual_explanation', 'gamification', 'simplification', 'challenge'],
        'system_prompt': 'Expert educational content adapter'
    },
    'LearningPathAgent': {
        'model': 'gemini-3.0-pro',
        'purpose': 'Optimizes lesson sequencing and pacing',
        'input': 'Emotion history + completed lessons + user profile',
        'output': 'Next lesson recommendation with reasoning',
        'system_prompt': 'Expert learning path optimizer'
    },
    'AssessmentAgent': {
        'model': 'gemini-3.0-pro',
        'purpose': 'Evaluates comprehension and identifies knowledge gaps',
        'input': 'Student responses + emotion data + time spent',
        'output': 'Comprehension score + knowledge gaps + recommendations',
        'system_prompt': 'Expert educational assessor'
    },
    'PersonalityAgent': {
        'model': 'gemini-3.0-flash',
        'purpose': 'Personalizes teaching tone and style',
        'input': 'User profile + current emotion + topic',
        'output': 'Personality parameters (tone, complexity, humor, etc.)',
        'system_prompt': 'Personality customization expert'
    }
}


def get_agent_info() -> dict:
    """
    Get information about all available agents.
    
    Returns:
        Dictionary with agent models and descriptions
    """
    return {
        'models': AGENT_MODELS,
        'descriptions': AGENT_DESCRIPTIONS,
        'total_agents': len(AGENT_MODELS),
        'flash_agents': [k for k, v in AGENT_MODELS.items() if 'flash' in v],
        'pro_agents': [k for k, v in AGENT_MODELS.items() if 'pro' in v]
    }


def verify_gemini_3_only() -> bool:
    """
    Verify that all agents use only Gemini 3 models.
    
    Returns:
        True if all agents use Gemini 3, False otherwise
    """
    for agent_name, model in AGENT_MODELS.items():
        if 'gemini-3' not in model:
            print(f"❌ {agent_name} uses invalid model: {model}")
            return False
    
    print("✅ All agents use Gemini 3 models")
    return True
