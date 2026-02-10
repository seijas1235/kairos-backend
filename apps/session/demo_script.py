"""
KAIROS Demo Script - Hackathon Final Version
Topic: Astrophysics - Black Holes and Event Horizon
Target: University student (20 years old)
Flow: Dense Theory → Confusion Detection → Multimodal Analogy (Video) → Eureka Moment
"""
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


async def run_demo_sequence(consumer):
    """
    FINAL HACKATHON DEMO: "EVENT HORIZON" SEQUENCE
    
    Demonstrates KAIROS's ability to:
    1. Present complex academic content
    2. Detect student confusion in real-time
    3. Adapt with simplified analogies + video
    4. Confirm understanding through emotion detection
    
    Target: University student (20 years old, Intro to Astrophysics)
    """
    try:
        logger.info("🚀 INICIANDO DEMO FINAL: SECUENCIA 'EVENT HORIZON'...")
        
        # --- SCENE 1: UNIVERSITY-LEVEL THEORY (The intellectual hook) ---
        logger.info("⏰ Pausa inicial de 3 segundos...")
        await asyncio.sleep(3)
        
        # 1.1 Learning Path (Mental map of the topic)
        logger.info("📤 Sending Learning Path: Astrophysics...")
        await consumer.send(text_data=json.dumps({
            "type": "learning_path",
            "data": {
                "topic": "Astrophysics: Singularities and the Event Horizon",
                "estimated_duration": "10 min",
                "nodes": [
                    {"id": 1, "title": "Theoretical Framework (General Relativity)", "status": "active"},
                    {"id": 2, "title": "The Curvature Analogy", "status": "locked"},
                    {"id": 3, "title": "Information Paradox", "status": "locked"}
                ]
            }
        }))
        logger.info("✅ Learning Path sent")
        
        await asyncio.sleep(2)
        
        # 1.2 First Content (Dense, academic, with stunning image)
        logger.info("📤 Sending initial theoretical content...")
        await consumer.send(text_data=json.dumps({
            "type": "lesson_content",
            "content": [
                {
                    "type": "text",
                    "content": "Hey Gustavo. To understand black holes at the university level, we need to stop thinking about 'gravity as a force' (Newton) and shift to 'gravity as geometry' (Einstein). A black hole is a region where spacetime curvature becomes infinite, creating a singularity."
                },
                {
                    "type": "image_prompt",
                    "content": "High-resolution visualization of deep space showing massive gravitational distortion, interstellar style, dark and blue colors.",
                    "image_url": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=2000&auto=format&fit=crop"
                }
            ]
        }))
        logger.info("✅ Theoretical content sent")
        
        # --- SCENE 2: THE CONFUSION (Your acting moment) ---
        # User should show confused expression when hearing "geometry"
        logger.info("👀 WAITING FOR USER REACTION (10 seconds to act confused)...")
        await asyncio.sleep(10)
        
        # Simulate real-time confusion detection
        logger.info("📤 Sending confusion detection...")
        await consumer.send(text_data=json.dumps({
            "type": "emotion_detected",
            "emotion": "confused",
            "confidence": 0.98,
            "message": "🤔 KAIROS notices that 'General Relativity' is a dense concept..."
        }))
        logger.info("✅ Confusion detected")
        
        # Dramatic processing pause
        logger.info("⏰ Dramatic processing pause (3 seconds)...")
        await asyncio.sleep(3)
        
        # 2.1 AI Adapts (The "WOW" moment: Simplification + Video)
        logger.info("📤 Sending multimodal adaptation (analogy + video)...")
        await consumer.send(text_data=json.dumps({
            "type": "lesson_content",
            "content": [
                {
                    "type": "text",
                    "content": "I see that confused look. That's normal, it's counterintuitive. 🛑 Forget the equations for a second. Let's use a classic visual analogy: imagine the universe not as empty space, but as a stretched elastic fabric."
                },
                {
                    "type": "video_url",
                    "content": "https://svs.gsfc.nasa.gov/vis/a010000/a013300/a013326/BH_Accretion_Disk_Sim_360_1080.mp4",
                    "caption": "🌌 Visualization: How mass curves the 'fabric' of spacetime"
                }
            ]
        }))
        logger.info("✅ Adaptive content with VIDEO sent")
        
        # --- SCENE 3: THE EUREKA MOMENT (Your smile) ---
        # User watches video and shows understanding
        logger.info("👀 WAITING FOR USER TO WATCH VIDEO (12 seconds)...")
        await asyncio.sleep(12)
        
        # Simulate happiness detection (user smiles and nods)
        logger.info("📤 Sending comprehension detection...")
        await consumer.send(text_data=json.dumps({
            "type": "emotion_detected",
            "emotion": "happy",
            "confidence": 0.96,
            "message": "💡 Excellent! Your expression indicates understanding."
        }))
        logger.info("✅ Comprehension detected")
        
        await asyncio.sleep(2)
        
        # Final reinforcement
        logger.info("📤 Sending final reinforcement...")
        await consumer.send(text_data=json.dumps({
            "type": "lesson_content",
            "content": [
                {
                    "type": "text",
                    "content": "Exactly! That's the key. A black hole doesn't 'suck' like a vacuum cleaner; it creates such a steep slope in that fabric that nothing, not even light, has enough energy to climb back up. Does the concept of 'Event Horizon' make more sense now?"
                }
            ]
        }))
        logger.info("✅ Final reinforcement sent")
        
        logger.info("🎬 ✅ SEQUENCE COMPLETED. READY TO CUT VIDEO.")
        
    except Exception as e:
        logger.error(f"❌ ERROR EN DEMO SCRIPT: {e}", exc_info=True)
