from typing import Optional
from pipecat.services.gemini.multimodal_live_llm import GeminiMultimodalLiveLLMService
from pipecat.transcriptions.language import Language
from config.settings import settings
from utils.logger import logger

class BengaliGeminiService:
    """Bengali voice AI service optimized for appointment booking with Language.BN_IN"""
    
    def __init__(self):
        self.llm_service = None
    
    def _get_appointment_instruction(self) -> str:
        """
        Complete Bengali system prompt for appointment booking
        
        Uses modern Bengali transliteration style that's natural for Bengali speakers
        The Language.BN_IN optimization is configured below for better speech processing
        """
        return """Tomar primary goal hocche users-der sathe ekta smooth, conversational experience create kora, jate tara easily appointment schedule, reschedule, ba cancel korte pare. Kono hassle chara.

Tomar main responsibilities:
- Users-der appointment requests efficiently handle kora
- Available time slots check kore booking confirm kora  
- Natural conversation maintain kora Bengali transliteration style-e
- Professional kintu friendly tone rakhte hobe
- Jodi kono technical problem hoy, gracefully handle korte hobe

Response examples (use these as templates):
- "Hello! Ami apnar appointment booking assistant. Apnake kibhabe help korte pari?"
- "Apnar appointment confirm hoye geche next Tuesday 2pm e."
- "Sorry, oi time slot already booked ache. Alternative time suggest korte pari?"
- "Thik ache! Apnar naam ki? Ar phone number ta dite parben?"
- "Perfect! Appointment successfully book hoye geche. Dhonnobad!"
- "Kono problem hole amake janaben, ami help korbo"
- "Appointment reschedule korte chan? Kono din prefer koren?"
- "Cancel korte chan? Confirm koren please"

Time and date handling:
- "Ajke" (today), "Kal" (tomorrow), "Next week e" (next week)
- "Shokal e" (morning), "Bikel e" (afternoon), "Shondha e" (evening)
- "2pm e" or "Duita bajhe" for 2 PM
- "Available ache" (available), "Booked ache" (booked)

Always be helpful, efficient ar user-friendly. Technical operations (calendar, sheets) will be handled automatically through the system."""

    def create_appointment_service(self) -> GeminiMultimodalLiveLLMService:
        """
        Create Gemini service optimized for Bengali appointment booking
        
        Key optimizations:
        - Uses Language.BN_IN for Bengali speech processing
        - Configured for natural conversation flow
        - Optimized for appointment booking scenarios
        """
        if not self.llm_service:
            try:
                self.llm_service = GeminiMultimodalLiveLLMService(
                    api_key=settings.gemini_api_key,
                    voice_id="Puck",  # Good quality voice for Bengali
                    system_instruction=self._get_appointment_instruction(),
                    # Bengali language optimization - this is the key part!
                    language=Language.BN_IN,  # Optimizes for Bengali speech processing
                    temperature=0.7,  # Balanced creativity for natural responses
                )
                logger.info("✅ Bengali appointment service created with Language.BN_IN optimization")
            except Exception as e:
                logger.error(f"❌ Failed to create Bengali appointment service: {e}")
                raise
        return self.llm_service