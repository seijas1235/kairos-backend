import json
import hashlib
from .base_agent import KairosAgent
from google.genai import types

class ContentAdapterAgent(KairosAgent):
    def get_model_name(self) -> str:
        return self.MODEL_PRO

    def _generate_image_url(self, prompt: str, index: int = 0) -> str:
        """
        Generate image URL. Uses picsum.photos for reliable placeholder images.
        """
        # Use picsum.photos which provides real images (no CORS issues)
        # Alternative: Generate with Gemini Imagen 3 in production
        
        # Use a seed based on the prompt for consistent images
        import hashlib
        seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 1000 + index
        
        return f"https://picsum.photos/seed/{seed}/800/500"

    async def process(self, input_data: dict) -> list:
        """
        Generates content based on user input, emotion, and style.
        Returns a LIST of JSON chunks with IMAGE URLS included.
        
        Each image_prompt chunk MUST include:
        - type: "image_prompt"
        - content: Text description (the prompt)
        - image_url: URL of the actual image to display
        - alt_text: Accessibility text
        """
        user_input = input_data.get("user_input", "")
        detected_emotion = input_data.get("detected_emotion", {})
        learning_style = input_data.get("style", "Visual") # Default to Visual if not specified

        # Special instruction for Mixed style
        style_instruction = ""
        if learning_style == "Mixto":
            style_instruction = "MANDATORY: You MUST interleave an 'image_prompt' chunk after every 2 'text' chunks."

        system_prompt = f"""
        You are the Content Adapter Agent.
        Your output must be a STRICT JSON list of chunks.
        NO markdown outside the JSON. NO plain text blocks.
        
        Chunk types allowed:
        - "text": Short explanation (max 40 words).
        - "image_prompt": Description for illustration (will be used to generate image).
        
        Format example:
        [
            {{"type": "text", "content": "Explanation part 1..."}},
            {{"type": "text", "content": "Explanation part 2..."}},
            {{"type": "image_prompt", "content": "Detailed visual description for image generation..."}}
        ]
        
        Style: {learning_style}
        {style_instruction}
        """
        
        prompt = f"""
        Context: User said "{user_input}".
        Detected emotion: {detected_emotion}.
        Generate the lesson content strictly following the JSON format.
        """

        # TODO: In production, call Gemini API here:
        # response = self.client.models.generate_content(
        #     model=self.model_name,
        #     contents=prompt,
        #     config=types.GenerateContentConfig(response_mime_type='application/json')
        # )
        # content_chunks = json.loads(response.text)
        
        # Mocking logic to simulate the 'Mixed' style behavior for verification
        mock_response = [
            {"type": "text", "content": f"Response to '{user_input}' regarding {learning_style} style."},
            {"type": "text", "content": "Here is the second point of information."},
        ]
        
        if learning_style == "Mixto":
            mock_response.append({
                "type": "image_prompt", 
                "content": "A diagram illustrating the previous points."
            })
            mock_response.append({"type": "text", "content": "Continuing with the third point."})
        
        # POST-PROCESS: Add image URLs to all image_prompt chunks
        processed_chunks = []
        image_index = 0
        
        for chunk in mock_response:
            if chunk["type"] == "image_prompt":
                # Generate image URL from the prompt
                image_url = self._generate_image_url(chunk["content"], image_index)
                image_index += 1
                
                processed_chunks.append({
                    "type": "image_prompt",
                    "content": chunk["content"],  # Keep the prompt for context
                    "image_url": image_url,       # 🔥 CRITICAL: URL to display
                    "alt_text": chunk["content"][:100]  # Accessibility
                })
            else:
                processed_chunks.append(chunk)
        
        return processed_chunks
