import asyncio
import json
import os
import uuid
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Pipecat imports
from pipecat.frames.frames import TranscriptionFrame, TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.gemini.multimodal_live_llm import GeminiMultimodalLiveLLMService
from pipecat.services.twilio import TwilioTransport
from pipecat.vad.silero import SileroVADAnalyzer
from pipecat.transcriptions.language import Language

# Local imports
from config.settings import settings
from services.gemini_service import BengaliGeminiService
from services.twilio_service import TwilioService
from services.n8n_service import N8nIntegrationService
from utils.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title="Bengali Appointment Agent",
    description="24/7 Bengali voice agent for appointment booking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

class N8nIntegrationProcessor(FrameProcessor):
    """Processes user speech and integrates with n8n for appointment booking"""
    
    def __init__(self, session_id: str, caller_id: str):
        super().__init__()
        self.session_id = session_id
        self.caller_id = caller_id
        self.n8n_service = N8nIntegrationService(session_id, caller_id)
    
    async def process_frame(self, frame, direction):
        """Process frames and handle n8n integration"""
        
        # Only process user transcriptions going upstream
        if isinstance(frame, TranscriptionFrame) and direction == FrameDirection.UPSTREAM:
            user_text = frame.text.strip()
            
            if user_text:
                logger.info(f"User said: {user_text}")
                
                # Send to n8n for appointment processing
                n8n_response = await self.n8n_service.send_to_n8n(
                    user_text, 
                    "user_message"
                )
                
                if n8n_response:
                    logger.info(f"n8n response: {n8n_response}")
                    # Enhance context with n8n response
                    enhanced_text = f"{user_text}\n\n[Appointment system response: {n8n_response}]"
                    frame.text = enhanced_text
        
        return frame

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("🚀 Bengali Appointment Agent starting up...")
    logger.info(f"Server running on port {settings.port}")
    logger.info(f"Twilio configured: {bool(settings.twilio_account_sid)}")
    logger.info(f"Gemini configured: {bool(settings.gemini_api_key)}")
    logger.info(f"n8n webhook: {settings.n8n_webhook_url}")
    logger.info("✅ Ready for 24/7 appointment booking!")

@app.post("/")
async def handle_twilio_call(request: Request):
    """
    Main Twilio webhook endpoint - handles all incoming calls
    This is where 24/7 appointment booking starts
    """
    try:
        logger.info("📞 Incoming call received")
        
        # Get call information from Twilio
        form_data = await request.form()
        call_info = TwilioService.extract_call_info(dict(form_data))
        
        logger.info(f"Call from {call_info['caller_id']}, SID: {call_info['call_sid']}")
        
        # Generate TwiML response to establish WebSocket connection
        twiml_response = await TwilioService.handle_incoming_call(request)
        
        logger.info("✅ TwiML response sent to Twilio")
        return twiml_response
        
    except Exception as e:
        logger.error(f"❌ Error handling Twilio call: {e}")
        # Return basic TwiML to avoid call failure
        return HTMLResponse(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, system temporarily unavailable.</Say></Response>',
            media_type="application/xml"
        )

@app.websocket("/ws/{call_sid}")
async def websocket_endpoint(websocket: WebSocket, call_sid: str):
    """
    WebSocket endpoint for real-time audio processing
    This handles the actual Bengali voice conversation
    """
    await websocket.accept()
    logger.info(f"🔌 WebSocket connected for call: {call_sid}")
    
    try:
        # Wait for Twilio start message
        start_message = await websocket.receive_text()
        start_data = json.loads(start_message)
        
        if start_data.get("event") == "start":
            # Extract call information
            stream_sid = start_data["start"]["streamSid"]
            custom_params = start_data["start"].get("customParameters", {})
            caller_id = custom_params.get("caller_id", "unknown")
            
            logger.info(f"📞 Call started - Stream: {stream_sid}, Caller: {caller_id}")
            
            # Create session
            session_id = str(uuid.uuid4())
            active_sessions[call_sid] = {
                "session_id": session_id,
                "stream_sid": stream_sid,
                "caller_id": caller_id,
                "websocket": websocket,
                "status": "active"
            }
            
            # Start the Bengali appointment agent
            await run_bengali_appointment_agent(websocket, session_id, stream_sid, caller_id, call_sid)
            
    except Exception as e:
        logger.error(f"❌ WebSocket error for call {call_sid}: {e}")
    finally:
        # Clean up session
        if call_sid in active_sessions:
            del active_sessions[call_sid]
        try:
            await websocket.close()
        except:
            pass
        logger.info(f"🔌 WebSocket disconnected for call: {call_sid}")

async def run_bengali_appointment_agent(websocket: WebSocket, session_id: str, stream_sid: str, caller_id: str, call_sid: str):
    """
    Main Bengali appointment booking agent
    This is the core 24/7 appointment booking logic
    """
    
    logger.info(f"🤖 Starting Bengali appointment agent for session {session_id}")
    
    try:
        # Initialize Bengali AI service with Language.BN_IN optimization
        gemini_service = BengaliGeminiService()
        llm = gemini_service.create_appointment_service()
        
        # Configure Twilio transport
        transport = TwilioTransport(
            account_sid=settings.twilio_account_sid,
            auth_token=settings.twilio_auth_token,
            websocket=websocket,
            stream_sid=stream_sid,
        )
        
        # Voice Activity Detection for natural conversation
        vad = SileroVADAnalyzer()
        
        # Create conversation context
        context = OpenAILLMContext()
        context_aggregator = llm.create_context_aggregator(context)
        
        # Create n8n integration processor
        n8n_processor = N8nIntegrationProcessor(session_id, caller_id)
        
        # Build the pipeline for appointment booking
        pipeline = Pipeline([
            transport.input(),           # Audio input from phone call
            vad,                        # Voice activity detection
            n8n_processor,              # n8n appointment booking integration
            llm,                        # Bengali AI response with Language.BN_IN
            transport.output(),         # Audio output to phone call
        ])
        
        # Create and configure pipeline task
        task = PipelineTask(pipeline)
        
        # Update session status
        active_sessions[call_sid]["status"] = "running"
        
        # Start with Bengali appointment greeting
        appointment_greeting = "Hello! Ami apnar appointment booking assistant. Apnake kibhabe help korte pari?"
        await task.queue_frames([TextFrame(appointment_greeting)])
        
        logger.info(f"🎤 Appointment greeting sent for session {session_id}")
        
        # Run the appointment booking pipeline
        runner = PipelineRunner()
        await runner.run(task)
        
    except Exception as e:
        logger.error(f"❌ Error in appointment agent for session {session_id}: {e}")
        active_sessions[call_sid]["status"] = "error"
    finally:
        active_sessions[call_sid]["status"] = "ended"
        logger.info(f"🏁 Appointment agent ended for session {session_id}")

# Health and monitoring endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway monitoring"""
    try:
        active_count = len(active_sessions)
        
        health_data = {
            "status": "healthy",
            "active_calls": active_count,
            "services": {
                "twilio": bool(settings.twilio_account_sid and settings.twilio_auth_token),
                "gemini": bool(settings.gemini_api_key),
                "n8n": bool(settings.n8n_webhook_url)
            },
            "environment": settings.environment
        }
        
        logger.debug(f"Health check: {active_count} active calls")
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/sessions")
async def get_active_sessions():
    """Get information about active appointment sessions"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": {
            call_sid: {
                "session_id": session["session_id"],
                "caller_id": session["caller_id"][-4:] if session["caller_id"] != "unknown" else "unknown",  # Privacy
                "status": session["status"]
            }
            for call_sid, session in active_sessions.items()
        }
    }

@app.get("/")
async def root():
    """Root endpoint - shows system status"""
    return {
        "service": "Bengali Appointment Agent",
        "status": "running",
        "active_calls": len(active_sessions),
        "description": "24/7 Bengali voice agent for appointment booking"
    }

# Background cleanup task
@app.on_event("startup")
async def start_background_tasks():
    """Start background maintenance tasks"""
    asyncio.create_task(cleanup_inactive_sessions())

async def cleanup_inactive_sessions():
    """Clean up inactive sessions periodically"""
    while True:
        try:
            # Clean up sessions older than 1 hour
            inactive_sessions = []
            
            for call_sid, session in active_sessions.items():
                # Remove sessions that have been inactive for too long
                if session.get("status") == "ended":
                    inactive_sessions.append(call_sid)
            
            for call_sid in inactive_sessions:
                if call_sid in active_sessions:
                    del active_sessions[call_sid]
                    logger.info(f"Cleaned up inactive session: {call_sid}")
            
            await asyncio.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Bengali Appointment Agent...")
    
    # Railway provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )