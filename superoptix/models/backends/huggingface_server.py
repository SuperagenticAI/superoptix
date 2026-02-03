"""
HuggingFace server implementation with OpenAI-compatible API for SuperOptiX.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class HuggingFaceServer:
    """HuggingFace server with OpenAI-compatible API."""

    def __init__(self, model_name: str, port: int = 8001):
        self.model_name = model_name
        self.port = port
        self.app = FastAPI(title="HuggingFace Server", version="1.0.0")
        self.model = None
        self.tokenizer = None
        self.pipeline = None

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes."""

        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "model": self.model_name}

        @self.app.get("/v1/models")
        async def list_models():
            return {
                "object": "list",
                "data": [
                    {
                        "id": self.model_name,
                        "object": "model",
                        "created": 0,
                        "owned_by": "huggingface",
                    }
                ],
            }

        # Root endpoint for LiteLLM compatibility
        @self.app.post("/")
        async def root_chat_completions(request: ChatCompletionRequest):
            return await chat_completions(request)

        # Alternative endpoint for LiteLLM compatibility
        @self.app.post("/chat/completions")
        async def alt_chat_completions(request: ChatCompletionRequest):
            return await chat_completions(request)

        @self.app.post("/v1/chat/completions")
        async def chat_completions(request: ChatCompletionRequest):
            try:
                if self.pipeline is None:
                    raise HTTPException(status_code=500, detail="Model not loaded")

                # Convert messages to text
                messages = request.messages
                if not messages:
                    raise HTTPException(status_code=400, detail="No messages provided")

                # Simple message formatting (can be improved)
                prompt = ""
                for msg in messages:
                    if msg.role == "user":
                        prompt += f"User: {msg.content}\n"
                    elif msg.role == "assistant":
                        prompt += f"Assistant: {msg.content}\n"
                    elif msg.role == "system":
                        prompt += f"System: {msg.content}\n"

                prompt += "Assistant: "

                # Generate response
                # Handle temperature=0.0 case (greedy decoding)
                if request.temperature == 0.0:
                    response = self.pipeline(
                        prompt,
                        max_length=len(self.tokenizer.encode(prompt))
                        + request.max_tokens,
                        do_sample=False,  # Greedy decoding
                        pad_token_id=self.tokenizer.eos_token_id,
                        truncation=True,
                    )
                else:
                    response = self.pipeline(
                        prompt,
                        max_length=len(self.tokenizer.encode(prompt))
                        + request.max_tokens,
                        temperature=request.temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        truncation=True,
                    )

                # Extract the generated text
                generated_text = response[0]["generated_text"]
                assistant_response = generated_text[len(prompt) :].strip()

                # Format response in OpenAI format
                return ChatCompletionResponse(
                    id="chatcmpl-123",
                    created=int(torch.tensor(0).item()),
                    model=request.model,
                    choices=[
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": assistant_response,
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    usage={
                        "prompt_tokens": len(self.tokenizer.encode(prompt)),
                        "completion_tokens": len(
                            self.tokenizer.encode(assistant_response)
                        ),
                        "total_tokens": len(
                            self.tokenizer.encode(prompt + assistant_response)
                        ),
                    },
                )

            except Exception as e:
                logger.error(f"Error in chat completion: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def load_model(self):
        """Load the HuggingFace model."""
        try:
            logger.info(f"Loading model: {self.model_name}")

            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16
                if torch.cuda.is_available()
                else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
            )

            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1,
            )

            logger.info(f"Model loaded successfully: {self.model_name}")

        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise

    def start(self):
        """Start the server."""
        try:
            # Load model first
            self.load_model()

            # Start server
            logger.info(f"Starting HuggingFace server on port {self.port}")
            uvicorn.run(self.app, host="127.0.0.1", port=self.port, log_level="info")

        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise


def start_huggingface_server(model_name: str, port: int = 8001):
    """Start a HuggingFace server with the specified model."""
    server = HuggingFaceServer(model_name, port)
    server.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start HuggingFace server")
    parser.add_argument("model_name", help="HuggingFace model name")
    parser.add_argument("--port", type=int, default=8001, help="Port to run server on")

    args = parser.parse_args()

    start_huggingface_server(args.model_name, args.port)
