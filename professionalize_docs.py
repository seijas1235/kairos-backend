import os
import re

def professionalize_text(text):
    # 1. Remove emojis (basic set commonly used here)
    emojis = ['🤖', '🏗️', '🎯', '🚀', '🔑', '📡', '📁', '🧪', '🎨', '🔐', '🚧', '📞', '🎉', '📊', '✨', '🔌', '🕹️', '🌍', '📦', '🏆', '😕', '😊', '🎬', '🔗', '💡', '🛑', '🌌', '👀', '🎭', '✅', '❌', '🏗', '🎯', '🚀', '🔑', '📡', '📁', '🧪', '🎨', '🔐', '🚧', '📞', '🎉', '📊', '✨', '🔌', '🕹', '🌍', '📦', '🏆', '😕', '😊', '🎬', '🔗', '💡', '🛑', '🌌', '👀', '🎭', '✅', '❌']
    for emoji in emojis:
        text = text.replace(emoji, '')
    
    # 2. Replace clinical/unverified claims
    # ADHD/Autism claim
    text = text.replace('Particularly effective for neurodivergent students (ADHD, Autism) who benefit from immediate feedback.', 
                        'Designed to support diverse learning styles by adapting explanations dynamically.')
    # Millisecond/Latency claims
    text = text.replace('Millisecond-level response times', 
                        'Designed for low-latency real-time interaction using WebSockets and asynchronous processing.')
    text = text.replace('<100ms latency', 
                        'Low-latency real-time interaction.')
    text = text.replace('Works flawlessly under network stress', 
                        'Robust real-time session management using WebSockets.')
    
    # 3. Micro-expressions
    text = text.replace('Micro-expressions detection', 
                        'Real-time visual signal analysis to infer learning-related states such as confusion or disengagement.')
    
    # 4. Standardize Gemini 3
    # Replace gemini-1.5 or gemini-2.0 with Gemini 3 (if found in text)
    text = re.sub(r'Gemini (1\.5|2\.0)', 'Gemini 3', text)
    
    return text

def process_readme(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = professionalize_text(content)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Processed: {path}")

# Run for both
process_readme('c:/kairos/kairos-backend/README.md')
process_readme('c:/kairos/kairos-frontend-v2/README.md')
