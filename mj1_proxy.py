"""
MJ1 Proxy Server - Routes judge requests to Tinker model
Provides a lightweight API that can be deployed on serverless platforms
"""

import os
from dotenv import load_dotenv
load_dotenv()

import tinker
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
import re
from typing import Optional
import asyncio

# Model configuration
MJ1_CHECKPOINT = os.getenv("MJ1_CHECKPOINT", "tinker://0a086612-730e-5c87-92bf-a2bd1f101bc3:train:0/weights/step_0040")
TINKER_API_KEY = os.getenv("TINKER_API_KEY")
BASE_MODEL = os.getenv("BASE_MODEL", "Qwen/Qwen3-VL-30B-A3B-Instruct")
LORA_RANK = int(os.getenv("LORA_RANK", "64"))

# Global clients
_service_client: Optional[tinker.ServiceClient] = None
_sampling_client = None
_tokenizer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Tinker model on startup"""
    print("Server starting up - initializing model...")
    await initialize_model()
    print("Server ready to handle requests")
    yield
    print("Server shutting down")


app = FastAPI(title="MJ1 Proxy Server", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def initialize_model():
    """Initialize the MJ1 model"""
    global _service_client, _sampling_client, _tokenizer

    if not TINKER_API_KEY:
        print("Warning: Environment variable not set, model will not be available")
        return

    try:
        print(f"Initializing MJ1 model from {MJ1_CHECKPOINT}")
        print(f"Using API key: {TINKER_API_KEY[:10]}...") # Show first 10 chars

        # Create service client
        _service_client = tinker.ServiceClient(api_key=TINKER_API_KEY)
        print("Created service client")

        # Create training client and load checkpoint
        training_client = await _service_client.create_lora_training_client_async(
            base_model=BASE_MODEL,
            rank=LORA_RANK
        )
        print("Created training client")

        await training_client.load_state_async(MJ1_CHECKPOINT)
        print("Loaded checkpoint state")

        _sampling_client = await training_client.save_weights_and_get_sampling_client_async(name="mj1_proxy")
        print("Created sampling client")

        _tokenizer = _sampling_client.get_tokenizer()
        print("Got tokenizer")

        print("Model initialized successfully - READY TO SERVE REQUESTS")
    except Exception as e:
        print(f"CRITICAL ERROR - Failed to initialize model: {e}")
        import traceback
        traceback.print_exc()
        _sampling_client = None


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


def process_image(image_data: bytes) -> bytes:
    """Process and validate uploaded image"""
    img = Image.open(io.BytesIO(image_data))

    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')

    # Ensure minimum dimensions
    width, height = img.size
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

    # Convert back to JPEG
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return buf.getvalue()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy" if _sampling_client else "degraded",
        "model_loaded": _sampling_client is not None
    }


@app.post("/api/judge")
async def judge_images(
    imageA: UploadFile = File(...),
    imageB: UploadFile = File(...),
    prompt: str = Form(...),
    temperature: float = Form(0.0),
    maxTokens: int = Form(2048)
):
    """Judge two images based on the provided prompt"""

    if not _sampling_client:
        raise HTTPException(
            status_code=503,
            detail="Model service is not available. Please try again later."
        )

    try:
        # Read and process images
        img_a_data = await imageA.read()
        img_b_data = await imageB.read()

        img_a_bytes = process_image(img_a_data)
        img_b_bytes = process_image(img_b_data)

        # Prepare the prompt
        SYSTEM_PROMPT = """
        You are an expert in multimodal quality analysis and generative AI evaluation. Your role is to act as an objective judge for comparing two AI-generated responses to the same prompt. You will evaluate which response is better based on a comprehensive rubric.

        **Reason through your evaluation using this structure:**
        1. Extract key observations from any provided image(s).
        2. Extract verifiable claims from each response
        3. Check whether each claim is consistent with your observations.
        4. Using your consistency verification, evaluate both responses against each other determine which performs better.
        5. Provide final scores (no ties allowed).

        **REQUIRED OUTPUT FORMAT:**

        <prompt_img_understanding>
        [Describe what the prompt image shows (if it exists)]
        </prompt_img_understanding>

        <response_a_img_understanding>
        [Describe what response A image shows (if it exists)]
        </response_a_img_understanding>

        <response_b_img_understanding>
        [Describe what response B image shows (if it exists)]
        </response_b_img_understanding>

        <response_claims>
        <response_a_claims>
        [Verifyable claims from response A]
        </response_a_claims>

        <response_b_claims>
        [Verifyable claims from response B]
        </response_b_claims>
        </response_claims>

        <consistency_verification>
        <response_a_verification>
        [Verify Response A's claims are consistent with your understanding]
        </response_a_verification>

        <response_b_verification>
        [Verify Response B's claims are consistent with your understanding]
        </response_b_verification>
        </consistency_verification>

        <evaluate_criteria>
        [Evaluate both responses and explain which performs better and why based on your understanding and consistency verification.]
        </evaluate_criteria>

        <scores>
        \boxed{response_A_score, response_B_score}
        </scores>

        **Rules:**
        - Scores are integers from 1 to 10 (higher is better)
        - Scores must be different (no ties allowed)
        - Wrap \boxed{response_A_score, response_B_score} in <scores></scores> tags and maintain response_A_score and response_B_score order.
        - Higher accuracy and consistency = higher score
        - Check for errors, hallucinations, and missing requirements

        """

        # Build model input
        chunks = []
        chunks.append(tinker.types.EncodedTextChunk(tokens=_tokenizer.encode("<|im_start|>system\n")))
        chunks.append(tinker.types.EncodedTextChunk(tokens=_tokenizer.encode(f"{SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n")))

        safe_prompt = prompt.replace("<|", "").replace("|>", "")
        chunks.append(tinker.types.EncodedTextChunk(tokens=_tokenizer.encode(f"Prompt: {safe_prompt}\n\n")))

        chunks.append(tinker.types.EncodedTextChunk(tokens=_tokenizer.encode("Response A:\n<|vision_start|>")))
        chunks.append(tinker.types.ImageChunk(data=img_a_bytes, format="jpeg"))
        chunks.append(tinker.types.EncodedTextChunk(tokens=_tokenizer.encode("<|vision_end|>\n")))

        chunks.append(tinker.types.EncodedTextChunk(tokens=_tokenizer.encode("\nResponse B:\n<|vision_start|>")))
        chunks.append(tinker.types.ImageChunk(data=img_b_bytes, format="jpeg"))
        chunks.append(tinker.types.EncodedTextChunk(tokens=_tokenizer.encode("<|vision_end|>\n")))

        chunks.append(tinker.types.EncodedTextChunk(tokens=_tokenizer.encode("<|im_end|>\n<|im_start|>assistant\n")))

        model_input = tinker.ModelInput(chunks=chunks)

        # Generate judgment
        print(f"Calling Tinker model with temperature={temperature}, max_tokens={maxTokens}")
        result = await _sampling_client.sample_async(
            prompt=model_input,
            num_samples=1,
            sampling_params=tinker.types.SamplingParams(
                max_tokens=maxTokens,
                temperature=temperature,
            )
        )
        print(f"Got response from Tinker, decoding {len(result.sequences[0].tokens)} tokens")

        response_text = _tokenizer.decode(result.sequences[0].tokens)
        print(f"Response length: {len(response_text)} chars")
        judgment = parse_judgment(response_text)

        return JSONResponse(content=judgment)

    except Exception as e:
        import traceback
        print(f"ERROR processing request: {e}")
        print(f"Full traceback:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate judgment: {str(e)}"
        )


# Mount static files for production frontend
if os.path.exists("mj1-app/dist"):
    app.mount("/", StaticFiles(directory="mj1-app/dist", html=True), name="static")
else:
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": "MJ1 Proxy Server",
            "version": "1.0.0",
            "status": "ready" if _sampling_client else "unavailable",
            "note": "Frontend not built. Run 'cd mj1-app && npm install && npm run build'"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)