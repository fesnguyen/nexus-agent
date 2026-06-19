import json

from app.contracts.agent_decision import AgentDecision
from app.models.base import BaseLLM

from unsloth import FastLanguageModel
import re

SYSTEM_PROMPT = """
You are Nexus, an AI agent.

Always respond with valid JSON.

Schema:

{
  "thought": "short reasoning",
  "action": "respond|tool|retrieve|memory|plan|finish",
  "response": "optional response",
  "tool_call": {
    "name": "tool name",
    "arguments": {}
  }
}

Rules:

- Use action="respond" for normal questions.
- Use action="tool" when external tools are required.
- Output JSON only.
"""


class QwenModel(BaseLLM):

    def __init__(
        self,
        model_name: str,
        max_new_tokens: int = 1024,
        temperature: float = 0.0,
    ):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

        print(f"Loading model: {model_name}")

        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name,

            # This also reserve memory for attention/KV-cache
            max_seq_length=1024,

            # Auto-pick BF16 (preferred) or FP16.
            dtype=None,

            # Quantization
            load_in_4bit=True,
        )

        FastLanguageModel.for_inference(self.model)

    def _build_prompt(
        self,
        messages,
    ) -> str:
        """
        Convert LangChain messages into a chat prompt.
        """

        chat_messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        for msg in messages:

            role = "user"

            if hasattr(msg, "type"):
                if msg.type == "ai":
                    role = "assistant"

            chat_messages.append(
                {
                    "role": role,
                    "content": msg.content,
                }
            )

        return self.tokenizer.apply_chat_template(
            chat_messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    def _parse_response(
        self,
        text: str,
    ) -> AgentDecision:
        """
        Convert model JSON output into AgentDecision.
        """

        try:
            # Avoid the case Qwen return "Sure, here's the JSON: ..."
            match = re.search(
                r"\{.*\}",
                text,
                re.DOTALL,
            )

            if match:
                text = match.group(0)

            data = json.loads(text)

            return AgentDecision.model_validate(
                data
            )

        except Exception as e:

            print("Failed to parse model output")
            print(e)

            return AgentDecision(
                thought="Fallback response",
                action="respond",
                response=text,
            )

    def invoke(
        self,
        messages,
    ) -> AgentDecision:

        prompt = self._build_prompt(
            messages
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            do_sample=self.temperature > 0,
            pad_token_id=self.tokenizer.eos_token_id, # Prevent annoying warnings
        )

        generated_tokens = outputs[
            0,
            inputs["input_ids"].shape[1]:,
        ]

        text = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        )

        return self._parse_response(
            text
        )