import logging
import json
from .emotion_agent import EmotionAgent
from .content_adapter_agent import ContentAdapterAgent
from .learning_path_agent import LearningPathAgent
from .assessment_agent import AssessmentAgent
from .personality_agent import PersonalityAgent

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Coordination center for the 5-Agent Architecture.
    Does NOT "think", only routes messages and manages flow.
    """

    def __init__(self):
        logger.info("=" * 60)
        logger.info("🎯 ORCHESTRATOR: Initializing 5-Agent System")
        logger.info("=" * 60)
        
        # Instantiate agents
        self.emotion_agent = EmotionAgent()
        self.content_adapter_agent = ContentAdapterAgent()
        self.learning_path_agent = LearningPathAgent()
        self.assessment_agent = AssessmentAgent()
        self.personality_agent = PersonalityAgent()
        
        # Track agent usage
        self.agent_usage_stats = {
            "EmotionAgent": 0,
            "ContentAdapterAgent": 0,
            "LearningPathAgent": 0,
            "AssessmentAgent": 0,
            "PersonalityAgent": 0
        }
        
        # Store user context for the entire session
        # This context is set on start_lesson and persists for all subsequent interactions
        self.user_context = {
            "language": "es",
            "age": 15,
            "user_alias": "Estudiante",
            "level": "intermediate",
            "style": "Visual",
            "topic": "General Topic"
        }
        
        logger.info("✅ All 5 agents initialized successfully")
        logger.info("=" * 60)

    async def process_websocket_message(self, message: dict) -> dict:
        """
        Main entry point from WebSocket Consumer with Q&A support.
        Routing Logic:
        - key 'frame' -> EmotionAgent
        - key 'start_lesson' -> LearningPathAgent
        - key 'user_question' -> Q&A Handler
        - key 'text' with 'terminar' -> AssessmentAgent
        """
        logger.info("=" * 60)
        logger.info("📨 ORCHESTRATOR: Processing incoming message")
        logger.info(f"Message keys: {list(message.keys())}")
        logger.info("=" * 60)
        
        response_data = {}

        # NEW: Handle user questions (interruptions)
        # Frontend can send 'user_question' OR 'question' field
        if 'user_question' in message or ('type' in message and message['type'] == 'user_question'):
            logger.info("❓ USER QUESTION detected")
            return await self._handle_user_question(message)

        # NEW: Handle session complete (final assessment)
        if 'type' in message and message['type'] == 'session_complete':
            logger.info("🏁 SESSION COMPLETE detected")
            return await self._handle_session_complete(message)

        # 1. Handle Frame (Emotion Detection)
        if 'frame' in message:
            logger.info("🎭 Routing to: EmotionAgent")
            self.agent_usage_stats["EmotionAgent"] += 1
            
            # Update context if frontend sends fresh data (prioriza datos del mensaje)
            if 'language' in message:
                self.user_context['language'] = message['language']
            if 'age' in message:
                self.user_context['age'] = message['age']
            if 'user_alias' in message:
                self.user_context['user_alias'] = message['user_alias']
            if 'difficulty' in message:
                self.user_context['level'] = message['difficulty']
            if 'style' in message:
                self.user_context['style'] = message['style']
            if 'topic' in message:
                self.user_context['topic'] = message['topic']
            
            emotion_result = await self.emotion_agent.process(message)
            
            # Return emotion result with proper 'type' field for frontend
            response_data['type'] = 'emotion_result'
            response_data['emotion'] = emotion_result
            logger.info(f"✅ EmotionAgent result: {emotion_result.get('emotion', 'N/A')}")
            
            # If there's accompanying text, or if emotion triggers it, we might generate content
            # For now, let's assume we proceed to content generation if text is present
            if 'text' in message:
                logger.info("📝 Text detected, routing to: ContentAdapterAgent")
                logger.info(f"   Using context: {self.user_context['language']} | Age {self.user_context['age']} | {self.user_context['user_alias']}")
                self.agent_usage_stats["ContentAdapterAgent"] += 1
                
                # Use updated context (prioriza datos frescos del mensaje)
                content_context = {
                    "user_input": message.get('text', ''),
                    "detected_emotion": emotion_result,
                    "style": self.user_context['style'],
                    "language": self.user_context['language'],
                    "age": self.user_context['age'],
                    "user_alias": self.user_context['user_alias']
                }
                content_chunks = await self.content_adapter_agent.process(content_context)
                logger.info(f"✅ ContentAdapterAgent generated {len(content_chunks)} chunks")
                
                # Check for termination keywords
                user_text = message.get('text', '').lower()
                if 'terminar' in user_text or 'finish' in user_text:
                    logger.info("🏁 Termination keyword detected, routing to: AssessmentAgent")
                    self.agent_usage_stats["AssessmentAgent"] += 1
                    
                    summary = await self.assessment_agent.generate_summary({})
                    response_data['lesson_summary'] = summary
                    logger.info("✅ AssessmentAgent generated summary")
                    
                    content_chunks.append({"type": "text", "content": "Entendido, terminamos por hoy. ¡Buen trabajo!"})

                # Apply Personality (use stored user context)
                logger.info("🎨 Routing to: PersonalityAgent (for all text chunks)")
                self.agent_usage_stats["PersonalityAgent"] += 1
                
                final_chunks = await self._apply_personality(
                    content_chunks, 
                    emotion_result, 
                    language=self.user_context['language'],
                    age=self.user_context['age'],
                    user_alias=self.user_context['user_alias']
                )
                response_data['content'] = final_chunks
                logger.info(f"✅ PersonalityAgent processed {len(final_chunks)} chunks")

        # 2. Handle Start Lesson
        elif 'start_lesson' in message:
            # IMPORTANT: Save user context for the entire session
            # Frontend sends: difficulty, topic, user_alias, style, age, language
            self.user_context = {
                "language": message.get('language', 'es'),
                "age": message.get('age', 15),
                "user_alias": message.get('user_alias', 'Estudiante'),
                "level": message.get('difficulty', message.get('level', 'intermediate')),  # Frontend uses 'difficulty'
                "style": message.get('style', 'Visual'),
                "topic": message.get('topic', 'General Topic')
            }
            
            logger.info("="*60)
            logger.info("💾 USER CONTEXT SAVED FOR SESSION")
            logger.info(f"   Language: {self.user_context['language']}")
            logger.info(f"   Age: {self.user_context['age']}")
            logger.info(f"   Alias: {self.user_context['user_alias']}")
            logger.info(f"   Level: {self.user_context['level']}")
            logger.info(f"   Style: {self.user_context['style']}")
            logger.info(f"   Topic: {self.user_context['topic'][:50]}...")
            logger.info("="*60)
            
            logger.info("🚀 Routing to: LearningPathAgent")
            self.agent_usage_stats["LearningPathAgent"] += 1
            
            # Pass user context to LearningPathAgent
            learning_path_input = {**message, **self.user_context}
            path_result = await self.learning_path_agent.process(learning_path_input)
            response_data['learning_path'] = path_result
            logger.info("✅ LearningPathAgent initialized path")
            
            # Immediately generate intro content using the user's TOPIC
            logger.info(f"📝 Routing to: ContentAdapterAgent (intro for topic: '{self.user_context['topic'][:50]}...')")
            logger.info(f"   Using session context: {self.user_context['language']} | Age {self.user_context['age']} | {self.user_context['user_alias']}")
            self.agent_usage_stats["ContentAdapterAgent"] += 1
            
            # Use stored user context
            content_context = {
                "user_input": self.user_context['topic'],  # USE THE ACTUAL TOPIC, not "Start Lesson"
                "detected_emotion": {"emotion": "neutral"},
                "style": self.user_context['style'],
                "language": self.user_context['language'],
                "age": self.user_context['age'],
                "user_alias": self.user_context['user_alias']
            }
            content_chunks = await self.content_adapter_agent.process(content_context)
            logger.info(f"✅ ContentAdapterAgent generated {len(content_chunks)} intro chunks")
            
            logger.info("🎨 Routing to: PersonalityAgent")
            self.agent_usage_stats["PersonalityAgent"] += 1
            
            # Use stored user context
            final_chunks = await self._apply_personality(
                content_chunks, 
                {"emotion": "neutral"},
                language=self.user_context['language'],
                age=self.user_context['age'],
                user_alias=self.user_context['user_alias']
            )
            response_data['content'] = final_chunks
            logger.info(f"✅ PersonalityAgent processed {len(final_chunks)} intro chunks")

        else:
            logger.warning("❓ Unknown message type received in Orchestrator")
            response_data['error'] = "Unknown message type"
        
        # Log usage stats
        logger.info("=" * 60)
        logger.info("📊 AGENT USAGE STATS (this session):")
        for agent_name, count in self.agent_usage_stats.items():
            status = "✅" if count > 0 else "⚪"
            logger.info(f"  {status} {agent_name}: {count} calls")
        logger.info("=" * 60)

        return response_data
    
    async def _handle_user_question(self, message: dict) -> dict:
        """
        Handle user interruption with a question using Gemini Pro.
        Input: {user_question: str OR question: str, context: [...]}
        Output: {type: "lesson_content", content: [{type: "tutor_answer", content: "..."]}}
        """
        # Frontend can send 'user_question' OR 'question' field
        question = message.get('user_question', message.get('question', ''))
        context = message.get('context', [])
        
        # Update context if frontend sends fresh data (prioriza datos del mensaje)
        if 'language' in message:
            self.user_context['language'] = message['language']
        if 'age' in message:
            self.user_context['age'] = message['age']
        if 'user_alias' in message:
            self.user_context['user_alias'] = message['user_alias']
        if 'difficulty' in message:
            self.user_context['level'] = message['difficulty']
        if 'style' in message:
            self.user_context['style'] = message['style']
        if 'current_topic' in message:
            self.user_context['topic'] = message['current_topic']
        
        logger.info(f"❓ [Orchestrator] User question: {question[:80]}...")
        self.agent_usage_stats["ContentAdapterAgent"] += 1
        
        # Build context string from conversation history
        context_text = ""
        if context:
            recent_context = context[-5:] if len(context) > 5 else context
            context_text = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}..." 
                for msg in recent_context
            ])
        
        # Use updated user context (prioriza datos frescos del mensaje)
        language_map = {
            'es': 'ESPAÑOL (Spanish)',
            'en': 'English',
            'pt': 'Português (Portuguese)',
            'fr': 'Français (French)'
        }
        response_language = language_map.get(self.user_context['language'], 'English')
        
        prompt = f"""You are an expert tutor answering a student's question during a lesson.

STUDENT PROFILE:
- Name: {self.user_context['user_alias']}
- Age: {self.user_context['age']} years old
- Level: {self.user_context['level']}
- Current Topic: {self.user_context['topic']}

RECENT CONVERSATION CONTEXT:
{context_text if context_text else 'No prior context'}

STUDENT QUESTION: {question}

Provide a clear, concise answer (max 100 words):
- Answer directly and helpfully in {response_language}
- Reference context if relevant
- Be encouraging and supportive
- Use a warm, friendly tone appropriate for a {self.user_context['age']}-year-old
- Address the student as {self.user_context['user_alias']}

Return ONLY the answer text, no JSON, no markdown.
"""
        
        try:
            # Use ContentAdapterAgent's client to call Gemini Pro
            from google.genai import types
            
            response = self.content_adapter_agent._generate_content(
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7
                )
            )
            
            # Validate response
            if not response or not response.text:
                logger.error("❌ [Orchestrator] Empty response from Gemini API")
                return {
                    "type": "lesson_content",
                    "content": [{
                        "type": "tutor_answer",
                        "content": "Lo siento, no pude generar una respuesta. ¿Puedes reformular tu pregunta?"
                    }]
                }
            
            answer = response.text.strip()
            
            # Remove quotes if present
            if answer.startswith('"') and answer.endswith('"'):
                answer = answer[1:-1]
            
            logger.info(f"✅ [Orchestrator] Generated answer ({len(answer)} chars)")
            
            return {
                "type": "lesson_content",
                "content": [{
                    "type": "tutor_answer",
                    "content": answer
                }]
            }
            
        except Exception as e:
            logger.error(f"❌ [Orchestrator] Error generating answer: {e}", exc_info=True)
            
            return {
                "type": "lesson_content",
                "content": [{
                    "type": "tutor_answer",
                    "content": "Lo siento, tuve un problema procesando tu pregunta. ¿Puedes reformularla?"
                }]
            }

    async def _handle_session_complete(self, message: dict) -> dict:
        """
        Handle session completion and final assessment.
        Input: {type: 'session_complete', sessionId: str, summary: {...}}
        Output: {type: 'session_assessment', assessment: {...}}
        """
        session_id = message.get('sessionId', 'unknown')
        summary = message.get('summary', {})
        
        logger.info(f"🏁 [Orchestrator] Session complete: {session_id}")
        logger.info(f"   Duration: {summary.get('duration', 0)}s")
        logger.info(f"   Total chunks: {summary.get('totalChunks', 0)}")
        logger.info(f"   Questions asked: {summary.get('questionsAsked', 0)}")
        
        self.agent_usage_stats["AssessmentAgent"] += 1
        
        # Call AssessmentAgent with full session data
        assessment_input = {
            "session_id": session_id,
            "summary": summary,
            "user_context": self.user_context,
            "agent_usage": self.agent_usage_stats
        }
        
        assessment_result = await self.assessment_agent.generate_summary(assessment_input)
        
        logger.info("✅ [Orchestrator] Session assessment complete")
        
        return {
            "type": "session_assessment",
            "assessment": assessment_result,
            "session_id": session_id
        }

    async def _apply_personality(self, chunks: list, emotion: dict, language: str = 'es', age: int = 15, user_alias: str = 'Estudiante') -> list:
        """Helper to pass text chunks through personality agent."""
        final_chunks = []
        for chunk in chunks:
            if chunk.get('type') == 'text':
                refined = await self.personality_agent.process({
                    "text": chunk['content'],
                    "emotion": emotion,
                    "language": language,
                    "age": age,
                    "user_alias": user_alias
                })
                # Assuming refined returns dict, update content
                chunk['content'] = refined.get('text', chunk['content'])
            final_chunks.append(chunk)
        return final_chunks
