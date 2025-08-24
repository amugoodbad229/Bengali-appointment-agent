import httpx
from config.settings import settings


async def post_to_n8n(payload: dict) -> dict:
    """Post a payload to the configured n8n webhook URL.

    This is a small, resilient helper that can be expanded with retries.
    """
    url = settings.n8n_webhook_url
    if not url:
        raise RuntimeError("n8n webhook URL is not configured")

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


__all__ = ["post_to_n8n"]
import asyncio
import json
from typing import Dict, Any, Optional
import aiohttp
from config.settings import settings
from utils.logger import logger

class N8nIntegrationService:
    """Handles appointment booking integration with n8n"""
    
    def __init__(self, session_id: str, caller_id: str):
        self.session_id = session_id
        self.caller_id = caller_id
        self.webhook_url = settings.n8n_webhook_url
        logger.info(f"N8n appointment service initialized for session {session_id}")
    
    async def send_to_n8n(self, user_message: str, message_type: str = "appointment_request") -> Optional[str]:
        """Send appointment request to n8n for processing"""
        try:
            current_time = asyncio.get_event_loop().time()
            
            # Payload optimized for appointment booking
            payload = {
                "session_id": self.session_id,
                "caller_id": self.caller_id,
                "message": user_message,
                "message_type": message_type,
                "timestamp": current_time,
                "service_type": "appointment_booking",
                "metadata": {
                    "language": "bengali" if self._is_bengali(user_message) else "english",
                    "intent": self._detect_intent(user_message)
                }
            }
            
            logger.info(f"📅 Sending appointment request to n8n: {user_message[:50]}...")
            
            # Send to n8n webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15),  # Longer timeout for appointment processing
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        n8n_response = await response.json()
                        logger.info(f"✅ n8n appointment response received")
                        
                        # Extract appointment response
                        appointment_response = n8n_response.get("response", "")
                        if appointment_response:
                            logger.info(f"📅 Appointment processed: {appointment_response[:50]}...")
                        
                        return appointment_response
                    else:
                        logger.error(f"❌ n8n appointment webhook error: {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"⏰ n8n appointment webhook timeout for session {self.session_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Error sending appointment request to n8n: {e}")
            return None
    
    def _is_bengali(self, text: str) -> bool:
        """Check if text contains Bengali characters"""
        bengali_range = range(0x0980, 0x09FF)
        return any(ord(char) in bengali_range for char in text)
    
    def _detect_intent(self, text: str) -> str:
        """Simple intent detection for appointment booking"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["appointment", "book", "schedule", "time", "date"]):
            return "book_appointment"
        elif any(word in text_lower for word in ["cancel", "reschedule", "change"]):
            return "modify_appointment"
        elif any(word in text_lower for word in ["confirm", "check", "status"]):
            return "check_appointment"
        else:
            return "general_inquiry"