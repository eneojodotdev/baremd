import os
import shutil
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from markitdown import MarkItDown
from openai import OpenAI

app = FastAPI(title="MarkItDown API")

# Setup Authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
BAREMD_API_KEY = os.environ.get("BAREMD_API_KEY")

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if not BAREMD_API_KEY:
        # If no key is configured on the server, fail securely
        raise HTTPException(status_code=500, detail="Server API key not configured")
    if api_key_header != BAREMD_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key_header

# Setup Rate Limiting (Keyed by the API Key header, fallback to IP if missing/failed)
def get_rate_limit_key(request: Request) -> str:
    key = request.headers.get(API_KEY_NAME)
    if key:
        return key
    return get_remote_address(request)

limiter = Limiter(key_func=get_rate_limit_key)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow CORS for the Next.js frontend (default dev server on 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MarkItDown with OCR Plugin enabled
api_key = os.environ.get("OPENAI_API_KEY")
llm_client = OpenAI(api_key=api_key) if api_key else None

md = MarkItDown(
    enable_plugins=True,
    llm_client=llm_client,
    llm_model="gpt-4o" if llm_client else None,
)

@app.post("/api/convert")
@limiter.limit("60/minute")
async def convert_file(request: Request, file: UploadFile = File(...), api_key: str = Depends(get_api_key)):
    try:
        # Create a temporary file to store the upload
        suffix = os.path.splitext(file.filename)[1] if file.filename else ""
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Convert the file using MarkItDown
        result = md.convert(temp_path)
        
        # Clean up the temporary file
        os.remove(temp_path)
        
        return {"filename": file.filename, "markdown": result.text_content}
        
    except Exception as e:
        # Clean up in case of error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
