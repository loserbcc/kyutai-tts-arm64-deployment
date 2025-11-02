#!/usr/bin/env python3
"""
Kyutai TTS FastAPI Server - Ready for MCP integration
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import tempfile
import os
import io
from pathlib import Path
from contextlib import asynccontextmanager

from kyutai_tts_api import KyutaiTTS, list_voices

# Global TTS instance
tts_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage model lifecycle"""
    global tts_instance
    print("Loading Kyutai TTS model...")
    tts_instance = KyutaiTTS()
    tts_instance.load_model()  # Pre-load model on startup
    print("Model loaded, server ready!")
    yield
    # Cleanup
    tts_instance = None

# Create FastAPI app
app = FastAPI(
    title="Kyutai TTS API",
    description="Fast, high-quality text-to-speech API using Kyutai's DSM model",
    version="1.0.0",
    lifespan=lifespan
)

# Pydantic models
class TTSRequest(BaseModel):
    text: str
    voice: str = "default"
    return_audio: bool = False
    
class TTSBatchRequest(BaseModel):
    texts: List[str]
    voice: str = "default"

class TTSResponse(BaseModel):
    success: bool
    duration: float
    sample_rate: int
    voice: str
    text_length: int
    audio_url: Optional[str] = None

class VoiceInfo(BaseModel):
    id: str
    path: str
    emotion: str

# Endpoints
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "Kyutai TTS API",
        "version": "1.0.0",
        "endpoints": {
            "POST /synthesize": "Generate speech from text",
            "POST /synthesize/stream": "Stream speech generation",
            "POST /synthesize/batch": "Generate multiple speeches",
            "GET /voices": "List available voices",
            "GET /health": "Check server status"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": tts_instance is not None,
        "device": "cuda" if tts_instance and tts_instance.device.type == "cuda" else "cpu"
    }

@app.get("/voices", response_model=List[VoiceInfo])
async def get_voices():
    """List available voices"""
    return list_voices()

@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    """
    Synthesize speech from text
    
    Returns either JSON metadata or audio file
    """
    if not tts_instance:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Generate audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            result = tts_instance.synthesize(
                text=request.text,
                voice=request.voice,
                output_path=tmp.name,
                return_audio=request.return_audio
            )
            
            if request.return_audio:
                # Return audio file directly
                return FileResponse(
                    tmp.name,
                    media_type="audio/wav",
                    filename=f"tts_output_{request.voice}.wav",
                    headers={
                        "X-Duration": str(result["duration"]),
                        "X-Sample-Rate": str(result["sample_rate"])
                    }
                )
            else:
                # Return metadata with download URL
                response = TTSResponse(
                    success=True,
                    duration=result["duration"],
                    sample_rate=result["sample_rate"],
                    voice=result["voice"],
                    text_length=result["text_length"],
                    audio_url=f"/download/{os.path.basename(tmp.name)}"
                )
                return response
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize/stream")
async def synthesize_stream(request: TTSRequest):
    """
    Stream synthesized speech
    
    Useful for real-time applications
    """
    if not tts_instance:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    def generate():
        # This would need the streaming implementation
        # For now, generate full audio and stream it
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            result = tts_instance.synthesize(
                text=request.text,
                voice=request.voice,
                output_path=tmp.name
            )
            
            # Stream the file
            with open(tmp.name, "rb") as f:
                while chunk := f.read(4096):
                    yield chunk
    
    return StreamingResponse(
        generate(),
        media_type="audio/wav",
        headers={
            "Content-Disposition": f'attachment; filename="stream_{request.voice}.wav"'
        }
    )

@app.post("/synthesize/batch")
async def synthesize_batch(request: TTSBatchRequest):
    """
    Synthesize multiple texts in batch
    
    Efficient for processing multiple texts
    """
    if not tts_instance:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        results = []
        for i, text in enumerate(request.texts):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                result = tts_instance.synthesize(
                    text=text,
                    voice=request.voice,
                    output_path=tmp.name
                )
                results.append({
                    "index": i,
                    "text_preview": text[:50] + "..." if len(text) > 50 else text,
                    "duration": result["duration"],
                    "audio_url": f"/download/{os.path.basename(tmp.name)}"
                })
        
        return {
            "success": True,
            "count": len(results),
            "total_duration": sum(r["duration"] for r in results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_audio(filename: str, background_tasks: BackgroundTasks):
    """Download generated audio files"""
    file_path = f"/tmp/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Clean up file after sending
    background_tasks.add_task(os.remove, file_path)
    
    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=filename
    )

# Run server
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get configuration from environment
    host = os.environ.get("TTS_HOST", "0.0.0.0")
    port = int(os.environ.get("TTS_PORT", "8899"))
    reload = os.environ.get("TTS_RELOAD", "true").lower() == "true"
    
    # In Docker, disable reload for production
    if os.environ.get("DOCKER_CONTAINER"):
        reload = False
    
    uvicorn.run(
        "kyutai_tts_server:app",
        host=host,
        port=port,
        reload=reload
    )