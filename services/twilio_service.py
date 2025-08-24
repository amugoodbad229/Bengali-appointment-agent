from typing import Any, Dict
from config.settings import settings


def send_sms(to: str, body: str) -> Dict[str, Any]:
    """Stub for sending SMS via Twilio.

    Replace with real Twilio client usage that reads `settings.twilio_account_sid`
    and `settings.twilio_auth_token`.
    """
    # TODO: implement real Twilio client call
    return {"to": to, "body": body, "status": "stub-sent"}


__all__ = ["send_sms"]
from typing import Dict, Any
from fastapi import Request
from fastapi.responses import HTMLResponse
from config.settings import settings
from utils.logger import logger

class TwilioService:
    """Handles Twilio integration for 24/7 phone calls"""
    
    @staticmethod
    async def handle_incoming_call(request: Request) -> HTMLResponse:
        """Handle incoming Twilio call and return TwiML for appointment booking"""
        
        # Get call information from Twilio
        form_data = await request.form()
        call_info = TwilioService.extract_call_info(dict(form_data))
        
        logger.info(f"📞 Appointment call from {call_info['caller_id']}, Call SID: {call_info['call_sid']}")
        
        # Get Railway app URL (Railway provides this automatically)
        railway_url = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "your-app.railway.app")
        websocket_url = f"wss://{railway_url}/ws/{call_info['call_sid']}"
        
        logger.info(f"Generated WebSocket URL: {websocket_url}")
        
        # Return TwiML that connects to our WebSocket for appointment booking
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Connect>
                <Stream url="{websocket_url}">
                    <Parameter name="caller_id" value="{call_info['caller_id']}" />
                    <Parameter name="call_sid" value="{call_info['call_sid']}" />
                    <Parameter name="purpose" value="appointment_booking" />
                </Stream>
            </Connect>
        </Response>"""
        
        logger.info(f"✅ TwiML sent for appointment booking call {call_info['call_sid']}")
        return HTMLResponse(content=twiml_response, media_type="application/xml")
    
    @staticmethod
    def extract_call_info(form_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract call information from Twilio webhook"""
        return {
            "caller_id": form_data.get("From", "unknown"),
            "call_sid": form_data.get("CallSid", "unknown"),
            "to_number": form_data.get("To", "unknown"),
            "call_status": form_data.get("CallStatus", "unknown"),
            "direction": form_data.get("Direction", "unknown"),
            "account_sid": form_data.get("AccountSid", "unknown")
        }