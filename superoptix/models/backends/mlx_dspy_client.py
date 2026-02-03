"""
Custom DSPy client for MLX models that works with local MLX servers
"""

import requests
import logging

from dspy.clients.base_lm import BaseLM

logger = logging.getLogger(__name__)


class MLXDSPyClient(BaseLM):
    """
    Custom DSPy client for MLX models that works with local MLX servers.

    This client calls MLX's server API directly, similar to how OllamaDirect works.
    """

    def __init__(
        self,
        model: str,
        api_base: str = "http://localhost:8000",
        temperature: float = 0.0,
        max_tokens: int = 4000,
        **kwargs,
    ):
        """
        Create a custom MLX DSPy client.

        Args:
            model: The MLX model name (e.g., "mlx-community/Llama-3.2-3B-Instruct-4bit")
            api_base: The MLX server base URL
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        """
        self.model = model
        self.api_base = api_base.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        self.history = []

    def forward(self, prompt=None, messages=None, **kwargs):
        """
        Forward pass through the MLX API.

        Args:
            prompt: Simple prompt string
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            Response in OpenAI format for compatibility
        """
        # Build messages
        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        # Merge kwargs
        request_kwargs = {**self.kwargs, **kwargs}

        # Build request payload for MLX server
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": request_kwargs.get("temperature", self.temperature),
            "max_tokens": request_kwargs.get("max_tokens", self.max_tokens),
        }

        # Add any additional parameters
        for key, value in request_kwargs.items():
            if key not in ["temperature", "max_tokens"]:
                payload[key] = value

        try:
            # Make direct API call to MLX server
            response = requests.post(
                f"{self.api_base}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120,  # 2 minute timeout
            )

            if response.status_code == 200:
                result = response.json()

                # Store in history for compatibility
                self.history.append({"messages": messages, "response": result})

                # Ensure all subfields are dicts/lists/primitives (should be by default)
                return result
            else:
                error_msg = f"MLX API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to MLX server: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    async def aforward(self, prompt=None, messages=None, **kwargs):
        """Async forward - currently just calls sync version"""
        return self.forward(prompt=prompt, messages=messages, **kwargs)

    def __call__(self, prompt=None, messages=None, **kwargs):
        """Make the client callable"""
        return self.forward(prompt=prompt, messages=messages, **kwargs)

    def copy(self, **kwargs):
        """Create a copy of this client with updated parameters"""
        new_kwargs = {**self.kwargs, **kwargs}
        return MLXDSPyClient(
            model=self.model,
            api_base=self.api_base,
            temperature=new_kwargs.get("temperature", self.temperature),
            max_tokens=new_kwargs.get("max_tokens", self.max_tokens),
            **{
                k: v
                for k, v in new_kwargs.items()
                if k not in ["temperature", "max_tokens"]
            },
        )

    def inspect_history(self, n: int = 1):
        """Inspect recent interactions"""
        return self.history[-n:] if self.history else []
