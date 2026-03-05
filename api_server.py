#!/usr/bin/env python3
"""MJ1 API Server - Image Comparison Judge"""

import asyncio
import io
import re
import os
import hashlib
import time
from pathlib import Path
from PIL import Image
from datetime import datetime
from typing import Optional, Dict, Any
from collections import defaultdict
import secrets

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

from dotenv import load_dotenv
load_dotenv()

# Environment configuration
API_PORT = int(os.getenv("API_PORT", "8000"))
API_HOST = os.getenv("API_HOST", "127.0.0.1")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Model configuration (optional)
TINKER_CHECKPOINT = os.getenv("TINKER_CHECKPOINT", "")
TINKER_API_KEY = os.getenv("TINKER_API_KEY", "")
API_KEY = os.getenv("API_KEY", "")
BASE_MODEL = os.getenv("BASE_MODEL", "Qwen/Qwen3-VL-30B-A3B-Instruct")
LORA_RANK = int(os.getenv("LORA_RANK", "64"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))

# Rate limiting configuration
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

# Demo mode when no API keys are configured
DEMO_MODE = not (TINKER_CHECKPOINT and API_KEY)

# Try to import tinker if available
try:
    if not DEMO_MODE:
        import tinker
        from tinker import types
        TINKER_AVAILABLE = True
    else:
        TINKER_AVAILABLE = False
except ImportError:
    TINKER_AVAILABLE = False
    DEMO_MODE = True

app = FastAPI(
    title="MJ1 Judge API",
    version="1.0.0",
    description="AI-powered image comparison judge",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.vercel.app", "localhost", "127.0.0.1"]
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400,
)

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.cleanup_interval = 300
        self.last_cleanup = time.time()

    def is_allowed(self, identifier: str) -> bool:
        current_time = time.time()

        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup()
            self.last_cleanup = current_time

        minute_ago = current_time - 60
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > minute_ago
        ]

        if len(self.requests[identifier]) >= RATE_LIMIT_PER_MINUTE:
            return False

        self.requests[identifier].append(current_time)
        return True

    def _cleanup(self):
        current_time = time.time()
        minute_ago = current_time - 60
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > minute_ago
            ]
            if not self.requests[identifier]:
                del self.requests[identifier]

rate_limiter = RateLimiter()
security = HTTPBearer(auto_error=False)

async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify API key if configured"""
    if not API_KEY:
        return None

    if not credentials:
        if not DEMO_MODE:
            raise HTTPException(status_code=403, detail="API key required")
        return None

    if not secrets.compare_digest(credentials.credentials, API_KEY):
        raise HTTPException(status_code=403, detail="Invalid API key")

    return credentials.credentials

async def get_client_identifier(request: Request) -> str:
    """Get client identifier for rate limiting"""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return hashlib.sha256(f"{client_ip}:{user_agent}".encode()).hexdigest()

# Model management
sampling_client = None
tokenizer = None

def log(msg: str):
    if ENVIRONMENT == "development":
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {msg}", flush=True)

def generate_error_response() -> dict:
    """Return error when Tinker is not available"""
    return {
        "error": True,
        "message": "Model service is not available. Please configure API keys to enable the service.",
        "winner": "N/A",
        "scoreA": 0,
        "scoreB": 0,
        "explanation": "Service unavailable",
        "fullResponse": ""
    }

def parse_judgment(response: str) -> dict:
    """Parse the model's judgment response"""
    response = response.replace('<|im_end|>', '').strip()

    scores_match = re.search(r'<scores>\s*\\?\\boxed\{(\d+),?\s*(\d+)\}\s*</scores>', response, re.DOTALL)
    if scores_match:
        score_a = int(scores_match.group(1))
        score_b = int(scores_match.group(2))
        winner = "A" if score_a > score_b else "B"
    else:
        match = re.search(r'\\?\\boxed\{(\d+),?\s*(\d+)\}', response, re.DOTALL)
        if match:
            score_a = int(match.group(1))
            score_b = int(match.group(2))
            winner = "A" if score_a > score_b else "B"
        else:
            score_a = 5
            score_b = 6
            winner = "B"

    explanation_match = re.search(r'<evaluate_criteria>(.*?)</evaluate_criteria>', response, re.DOTALL)
    explanation = explanation_match.group(1).strip() if explanation_match else "Based on the evaluation criteria."

    return {
        "winner": winner,
        "scoreA": score_a,
        "scoreB": score_b,
        "explanation": explanation,
        "fullResponse": response
    }

def validate_and_process_image(image_data: bytes, field_name: str) -> bytes:
    """Validate and process uploaded image"""
    if len(image_data) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"{field_name} exceeds maximum size of {MAX_IMAGE_SIZE_MB}MB"
        )

    try:
        img = Image.open(io.BytesIO(image_data))
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image format for {field_name}"
        )

    width, height = img.size
    if width > 4096 or height > 4096:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} dimensions too large (max 4096x4096)"
        )

    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')

    if width < 32 or height < 32:
        min_dim = 32
        if width < min_dim:
            new_width = min_dim
            new_height = max(min_dim, int(height * min_dim / width))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        if height < min_dim:
            new_height = min_dim
            new_width = max(min_dim, int(width * min_dim / height))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return buf.getvalue()

async def initialize_model():
    """Initialize the Tinker model if available"""
    global sampling_client, tokenizer

    if DEMO_MODE:
        log("Service unavailable - API keys not configured")
        return

    if not TINKER_AVAILABLE:
        log("Tinker module not available - service unavailable")
        return

    try:
        log(f"Initializing MJ1 model...")

        if TINKER_API_KEY:
            service_client = tinker.ServiceClient(api_key=TINKER_API_KEY)
            log("Using Tinker API")
        else:
            service_client = tinker.ServiceClient()
            log("Using local weights")

        training_client = await service_client.create_lora_training_client_async(
            base_model=BASE_MODEL,
            rank=LORA_RANK
        )

        await training_client.load_state_async(TINKER_CHECKPOINT)
        sampling_client = await training_client.save_weights_and_get_sampling_client_async(name="mj1_api")
        tokenizer = sampling_client.get_tokenizer()

        log("Model ready")
    except Exception as e:
        log(f"Failed to initialize model: {e}")
        log("Service unavailable")

@app.on_event("startup")
async def startup_event():
    await initialize_model()

@app.post("/api/judge")
async def judge_images(
    request: Request,
    imageA: UploadFile = File(...),
    imageB: UploadFile = File(...),
    prompt: str = Form(...),
    temperature: float = Form(0.0),
    maxTokens: int = Form(2048),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Judge two images based on the provided prompt"""

    client_id = await get_client_identifier(request)

    if not DEMO_MODE and not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_PER_MINUTE} requests per minute."
        )

    if len(prompt) > 1000:
        raise HTTPException(status_code=400, detail="Prompt too long (max 1000 characters)")

    temperature = max(0, min(1, temperature))
    maxTokens = max(100, min(4096, maxTokens))

    log(f"Judgment request from {client_id[:8]}...")

    try:
        img_a_data = await imageA.read()
        img_b_data = await imageB.read()

        img_a_bytes = validate_and_process_image(img_a_data, "Image A")
        img_b_bytes = validate_and_process_image(img_b_data, "Image B")

        if DEMO_MODE or not sampling_client:
            log("Model service not available")
            return JSONResponse(
                status_code=503,
                content=generate_error_response()
            )

        # Real model inference
        SYSTEM_PROMPT = """You are an expert judge for comparing two AI-generated responses.

Evaluate which response is better based on:
1. faithfulness_to_prompt: Adherence to requirements
2. text_image_alignment: Consistency between elements
3. overall_quality: Technical quality and coherence

Output format:
<evaluate_criteria>
[Evaluation explanation]
</evaluate_criteria>

<scores>
\\boxed{response_A_score, response_B_score}
</scores>

Rules: Scores are 1-10, must be different (no ties)."""

        chunks = []
        chunks.append(types.EncodedTextChunk(tokens=tokenizer.encode("<|im_start|>system\n")))
        chunks.append(types.EncodedTextChunk(tokens=tokenizer.encode(f"{SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n")))

        safe_prompt = prompt.replace("<|", "").replace("|>", "")
        chunks.append(types.EncodedTextChunk(tokens=tokenizer.encode(f"Prompt: {safe_prompt}\n\n")))

        chunks.append(types.EncodedTextChunk(tokens=tokenizer.encode("Response A:\n<|vision_start|>")))
        chunks.append(types.ImageChunk(data=img_a_bytes, format="jpeg"))
        chunks.append(types.EncodedTextChunk(tokens=tokenizer.encode("<|vision_end|>\n")))

        chunks.append(types.EncodedTextChunk(tokens=tokenizer.encode("\nResponse B:\n<|vision_start|>")))
        chunks.append(types.ImageChunk(data=img_b_bytes, format="jpeg"))
        chunks.append(types.EncodedTextChunk(tokens=tokenizer.encode("<|vision_end|>\n")))

        chunks.append(types.EncodedTextChunk(tokens=tokenizer.encode("<|im_end|>\n<|im_start|>assistant\n")))

        model_input = tinker.ModelInput(chunks=chunks)

        log("Generating judgment...")
        result = await sampling_client.sample_async(
            prompt=model_input,
            num_samples=1,
            sampling_params=types.SamplingParams(
                max_tokens=maxTokens,
                temperature=temperature,
            )
        )

        response_text = tokenizer.decode(result.sequences[0].tokens)
        judgment = parse_judgment(response_text)

        log(f"Judgment complete: Winner={judgment['winner']}")
        return JSONResponse(content=judgment)

    except HTTPException:
        raise
    except Exception as e:
        log(f"ERROR: {str(e)}")

        if DEMO_MODE:
            return JSONResponse(
                status_code=503,
                content=generate_error_response()
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate judgment. Please try again."
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MJ1 Judge API",
        "version": "1.0.0",
        "status": "unavailable" if DEMO_MODE else "ready",
        "message": "Service requires API configuration" if DEMO_MODE else "Service ready"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "degraded" if DEMO_MODE else "healthy",
        "model_loaded": sampling_client is not None,
        "environment": ENVIRONMENT,
        "service_available": not DEMO_MODE
    }

if __name__ == "__main__":
    if ENVIRONMENT == "production":
        uvicorn.run(
            app,
            host=API_HOST,
            port=API_PORT,
            log_level="warning",
            access_log=False,
        )
    else:
        log(f"Starting MJ1 server on http://{API_HOST}:{API_PORT}")
        log(f"Status: {'SERVICE UNAVAILABLE - Configure API keys' if DEMO_MODE else 'READY'}")
        uvicorn.run(app, host=API_HOST, port=API_PORT)