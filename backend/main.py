import os
import shutil
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from markitdown import MarkItDown
from openai import OpenAI

app = FastAPI(title="MarkItDown API")

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
async def convert_file(file: UploadFile = File(...)):
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
