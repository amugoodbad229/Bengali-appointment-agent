import os
import asyncio
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

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

# Simple in-memory storage
active_sessions: Dict[str, Any] = {}

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    print("🚀 Bengali Appointment Agent starting up...")
    print(f"Server running on port {os.environ.get('PORT', 8000)}")
    print("✅ Ready for 24/7 appointment booking!")

@app.post("/")
async def handle_twilio_call(request: Request):
    """Main Twilio webhook endpoint"""
    try:
        print("📞 Incoming call received")
        
        # Get Railway app URL
        railway_url = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "your-app.railway.app")
        
        # Return basic TwiML with Bengali responses
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice">Hello! Ami apnar appointment booking assistant. Dhonnobad for calling!</Say>
            <Pause length="2"/>
            <Say voice="alice">Apnar appointment er jonno amader website e jaan ba abar call korun.</Say>
        </Response>"""
        
        print("✅ TwiML response sent to Twilio")
        return HTMLResponse(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"❌ Error handling Twilio call: {e}")
        return HTMLResponse(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, system temporarily unavailable.</Say></Response>',
            media_type="application/xml"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway monitoring"""
    return {
        "status": "healthy",
        "active_calls": len(active_sessions),
        "services": {
            "twilio": bool(os.environ.get("TWILIO_ACCOUNT_SID")),
        },
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "production")
    }

@app.get("/")
async def root():
    """Root endpoint - shows system status"""
    return {
        "service": "Bengali Appointment Agent",
        "status": "running",
        "active_calls": len(active_sessions),
        "description": "24/7 Bengali voice agent for appointment booking",
        "railway_domain": os.environ.get("RAILWAY_PUBLIC_DOMAIN", "not-set")
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Bengali Appointment Agent...")
    
    # Railway provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )