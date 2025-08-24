from typing import Any, Dict
from config.settings import settings


async def generate_bengali_response(prompt: str) -> Dict[str, Any]:
    """Stub for calling the Bengali AI (Gemini) service.

    Replace the body of this function with a real HTTP/SDK call that uses
    `settings.gemini_api_key`.
    """
    # TODO: implement real API call using settings.gemini_api_key
    return {"prompt": prompt, "response": "(stub) Bengali response"}


__all__ = ["generate_bengali_response"]
from typing import Optional
from pipecat.services.gemini.multimodal_live_llm import GeminiMultimodalLiveLLMService
from config.settings import settings
from utils.logger import logger

class BengaliGeminiService:
    """Bengali voice AI service optimized for appointment booking"""
    
    def __init__(self):
        self.llm_service = None
    
    def _get_appointment_instruction(self) -> str:
        """System instruction optimized for appointment booking"""
        return """Ami apnar appointment booking assistant. Ami 24/7 available achi appointment book korar jonno.

Key instructions:
1. Always greet: "Hello! আমি আপনার appointment booking assistant। আপনি কোন দিন আর সময়ে appointment নিতে চান?"
2. Speak naturally mixing Bengali and English like: "Apnar appointment ta confirm hoye geche next Tuesday 2pm e"
3. Focus on collecting appointment information:
   - Name (naam)
   - Date preference (kon din)
   - Time preference (ki shomoy)
   - Contact number (phone number)
   - Service needed (ki service lagbe)

4. Be efficient and friendly
5. Confirm all details before booking
6. Always end with: "Apnar appointment confirm hoye geche. Dhonnobad!"

You have access to calendar and booking tools that work automatically. When you have enough information, the system will book the appointment automatically.

Remember: Keep conversation natural, efficient, and focused on appointment booking."""

    def create_appointment_service(self) -> GeminiMultimodalLiveLLMService:
        """Create Gemini service optimized for appointment booking"""
        if not self.llm_service:
            try:
                self.llm_service = GeminiMultimodalLiveLLMService(
                    api_key=settings.gemini_api_key,
                    voice_id="Puck",  # Good quality voice for Bengali
                    system_instruction=self._get_appointment_instruction(),
                )
                logger.info("Bengali appointment service created successfully")
            except Exception as e:
                logger.error(f"Failed to create Bengali appointment service: {e}")
                raise
        return self.llm_service