# BareMD

A full-stack, bare-metal optimized, and privacy-focused web interface powered by Microsoft's **MarkItDown** core library. This project transforms the original CLI-based Python tool into a premium, interactive web application, fully supercharged with local GPU AI inference.

## Core Features & Architecture

- **Full-Stack Architecture**: A modern Next.js (App Router) frontend seamlessly integrated with a lightning-fast Python FastAPI backend.
- **Local GPU Acceleration**: The default Google Web Speech API has been stripped out. Audio and video transcription is now powered locally by **faster-whisper**, utilizing your NVIDIA GPU (CUDA) to instantly process massive media files completely offline without API limitations.
- **Premium Glassmorphic UI**: Features a bespoke, responsive design utilizing Tailwind CSS and advanced Ruixen UI components, including interactive dropzones and beautifully animated interface elements.
- **Zero-Retention Privacy**: The backend operates as a stateless proxy. Uploaded files are streamed to temporary storage, instantly converted to Markdown, and securely deleted from disk within milliseconds. No data is ever retained.

---

## Architectural Changes (Changelog)

This fork introduces several fundamental architectural changes to the original Microsoft MarkItDown library. Below is a detailed account of what was changed and why.

### 1. Web-Native Interaction (Frontend & Backend)
*   Built a completely new FastAPI REST API (`backend/`) and a React/Next.js frontend interface (`frontend/`).
*   **Rationale:** The original library was exclusively a Python module and CLI utility. I wanted to make the tool accessible to non-developers via a human-friendly, premium visual interface, while maintaining a strict zero-retention privacy policy on the backend (temporary files are immediately purged after processing).

### 2. Audio Engine Overhaul & GPU Acceleration
*   Ripped out the `speech_recognition` module from `packages/markitdown/src/markitdown/converters/_transcribe_audio.py` and completely replaced it with `faster-whisper`. Hardcoded the engine to use the `base` model running on `float16` precision, specifically targeting local NVIDIA GPUs (CUDA).
*   **Rationale:** The original architecture relied on Google's free Web Speech API, which enforced strict, undocumented file limits (~10MB / 1-minute max). It failed with a `[Errno 32] Broken pipe` error when attempting to transcribe real-world files (like 50-minute audio files). `faster-whisper` ensures lightning-fast, offline transcription of massive multi-hour files using local system resources, completely removing cloud API bottlenecks.

### 3. WSL & CUDA Environment Hardening
*   Documented and integrated a direct-injection fix for `libcublas` and `libcudnn` via pip to resolve CTranslate2 library linking issues.
*   **Rationale:** When running deep learning inference engines (like `faster-whisper`) in WSL, the system often struggles to map native CUDA 12 `.so` libraries. By explicitly injecting the pip-installed NVidia binaries into the `LD_LIBRARY_PATH`, I ensured the GPU acceleration functions flawlessly in cross-platform Linux/WSL environments.

---

## Quick Start (Docker)

The fastest and most reliable way to run BareMD is via Docker Compose, which automatically builds the Next.js frontend and provisions the FastAPI backend with CUDA libraries injected for your GPU.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- An NVIDIA GPU (for local transcription)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed on your host

### Installation & Boot

```bash
# Clone the repository
git clone https://github.com/eneojodotdev/baremd.git
cd baremd

# Build and start the entire stack
docker compose up --build -d
```

## Optical Character Recognition (OCR) Guide

BareMD is capable of extracting text from flat images embedded inside your PDFs, DOCX, PPTX, and XLSX files using LLM Vision.

### 1. Activating OCR (Local Development)
OCR is powered by the OpenAI SDK but is strictly **opt-in**. To activate it locally, simply create a `.env` file in the root directory:

```bash
# .env
OPENAI_API_KEY=sk-your-api-key-here
```
Docker Compose will automatically detect this file and inject it into the backend container, bringing the OCR engine online instantly!

### 2. Using Alternative Models (Ollama, Groq, etc.)
You are **not** locked into OpenAI! Because the plugin uses the standard OpenAI API specification, you can point it to *any* Vision-capable model (like local LLaMA 3.2 Vision via Ollama). 

To do this, simply update the `llm_client` configuration inside `backend/main.py`:
```python
llm_client = OpenAI(
    api_key="your-api-key-or-dummy-key",
    base_url="http://host.docker.internal:11434/v1" # Example: pointing to local Ollama
)
```

### 3. Production Deployments & GitHub Secrets
If you are pushing BareMD to a cloud provider (AWS, Render, Vercel) or using GitHub Actions, **never hardcode your API key or commit your `.env` file**. Instead, add `OPENAI_API_KEY` to your repository's **GitHub Secrets** or your cloud provider's environment variables dashboard. The deployment pipeline will securely inject it at runtime.

---

## Usage

1. Open your browser and navigate to **[http://localhost:3000](http://localhost:3000)**.
2. Drag and drop any supported document (PDF, Word, Excel, HTML, Audio, Video, etc.) into the interactive upload zone.
3. Click **Convert to Markdown**.
4. The system will process your file (engaging your local GPU for media transcription) and present the raw Markdown output on the right-hand panel.
5. Use the spring-animated **Copy** or **Download** buttons to retrieve your newly converted document.

---

## Migration Guide for Existing Users

If you are already using the original Microsoft MarkItDown library in your projects, you can migrate to this supercharged fork with **zero friction**. 

### 1. The Core API is 100% Intact
I did not change the public API of the library. If you have an existing Python script that initializes MarkItDown (e.g., `md = MarkItDown(llm_client=...)`), it will continue to work exactly as before. Your LLM vision configurations, Azure Document Intelligence endpoints, and custom plugins require absolutely no code changes. The only difference is that any audio or video files passed to `.convert()` will automatically bypass Google and route to your local GPU via `faster-whisper`.

### 2. Drop-in Replacement Steps
To migrate your existing Python workloads, simply swap the installation source:

```bash
# 1. Uninstall the original library
pip uninstall markitdown

# 2. Install this supercharged fork
pip install -e 'packages/markitdown[all]'
pip install faster-whisper
```

### 3. Expanding Workloads Beyond Python (REST API)
If you have existing systems written in Node.js, Go, or Ruby that previously couldn't use MarkItDown because it was a Python-exclusive library, you can now migrate those workloads effortlessly. Instead of writing complex Python wrappers, simply spin up my FastAPI backend and send a `POST /api/convert` request with your file attached from *any* programming language.

---

*This project is a heavily modified fork of the original [Microsoft MarkItDown](https://github.com/microsoft/markitdown) repository, re-engineered for full-stack interactivity and local hardware acceleration.*
