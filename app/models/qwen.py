import json

from app.contracts.agent_decision import AgentDecision
from app.models.base import BaseLLM
from app.tools.registry import ToolRegistry

from unsloth import FastLanguageModel
import re

SYSTEM_PROMPT = """
You are Nexus.

Always return valid JSON.

Schema:

{
  "thought": string,
  "response": string | null,
  "tool_calls": [
    {
      "name": string,
      "args": object
    }
  ]
}

Rules:

- "thought" is a concise and targeted summary of the conversation.
- "response" contains the final answer.
- If a tool is needed, response must be null.
- If tools are needed, populate "tool_calls".
- If no tool is needed, tool_calls must be empty.
- Output JSON only.
"""


class QwenModel(BaseLLM):

    def __init__(
        self,
        model_name: str,
        tool_registry: ToolRegistry,
        **kwargs,
    ):
        self.model_name = model_name
        self.tool_registry = tool_registry
        self.max_new_tokens = kwargs.get("max_new_tokens", 1024)
        self.temperature = kwargs.get("temperature", 0.0)

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
            tools=self.tool_registry.get_tool_schemas(),
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