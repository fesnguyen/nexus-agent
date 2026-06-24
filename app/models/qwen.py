import json
from typing import Type

from pydantic import BaseModel, Field

from unsloth import FastLanguageModel
from app.contracts.agent_decision import AgentDecision
from app.models.base import BaseLLM
from app.tools.registry import ToolRegistry

import re


class QwenModel(BaseLLM):

    def __init__(
        self,
        model_name: str,
        **kwargs,
    ):
        self.model_name = model_name
        self.max_new_tokens = kwargs.get("max_new_tokens", 2048)
        self.temperature = kwargs.get("temperature", 0.0)

        print(f"Loading model: {model_name}")

        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name,

            # This also reserve memory for attention/KV-cache
            max_seq_length=2048,

            # Auto-pick BF16 (preferred) or FP16.
            dtype=None,

            # Quantization
            load_in_4bit=True,
        )

        FastLanguageModel.for_inference(self.model)

    def _build_prompt(
        self,
        messages,
        tool: ToolRegistry,
    ) -> str:
        """
        Convert LangChain messages into a chat prompt.
        """

        chat_messages = []

        for msg in messages:

            role = "user"

            if msg.type == "system":
                role = "system"

            elif msg.type == "ai":
                role = "assistant"

            elif msg.type == "tool":
                role = "tool"

            chat_messages.append(
                {
                    "role": role,
                    "content": msg.content,
                }
            )

        return self.tokenizer.apply_chat_template(
            chat_messages,
            tools=tool.get_tool_schemas(),
            tokenize=False,
            add_generation_prompt=True,
        )

    def _parse_response(
        self,
        text: str,
        response_model: Type[BaseModel],
    ) -> BaseModel:
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

            return response_model.model_validate(
                data
            )

        except Exception as e:

            print("Failed to parse model output")
            print(e)

            return response_model()

    def invoke(
        self,
        messages,
        tool: ToolRegistry,
        response_model: Type[BaseModel] = AgentDecision,
    ) -> BaseModel:

        prompt = self._build_prompt(
            messages,
            tool,
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            use_cache=True,
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
            text,
            response_model
        )