import json
from typing import Type

from pydantic import BaseModel, Field

from app.contracts.agent_decision import AgentDecision
from app.memory.conversation.conversation_schemas import Attachment
from app.models.base import BaseLLM
from app.tools.registry import ToolRegistry

from unsloth import FastLanguageModel
import re


class UnslothModel(BaseLLM):

    def __init__(
        self,
        model_name: str,
        **kwargs,
    ):
        self.model_name = model_name
        self.max_new_tokens = kwargs.get("max_new_tokens", 512)
        self.max_seq_length = kwargs.get("max_seq_length", self.max_new_tokens * 16)
        self.temperature = kwargs.get("temperature", 0.0)
        self.max_retries = kwargs.get("max_retries", 3)

        print(f"Loading model: {model_name}")

        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name,

            # This also reserve memory for attention/KV-cache
            max_seq_length=1024 * 4,

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
        attachments: list[Attachment],
    ) -> str:
        """
        Convert LangChain messages into a chat prompt.
        """

        chat_messages = []

        attachment_index = 0

        for msg in messages:

            role = "user"

            if msg.type == "system":
                role = "system"

            elif msg.type == "ai":
                role = "assistant"

            elif msg.type == "tool":
                role = "tool"

            content = msg.content

            # Attach extracted image context to the user message.
            if role == "user":
                # As the flow, message_id for every user messages are a MUST
                message_id = msg.additional_kwargs["message_id"]

                while (
                    attachment_index < len(attachments)
                    and attachments[attachment_index].message_id == message_id
                ):
                    attachment = attachments[attachment_index]

                    content += (
                        "\n\n"
                        f"[Attachment {attachment_index + 1}: {attachment.type.capitalize()}]\n"
                        f"{attachment.extracted_content}\n"
                    )

                    attachment_index += 1

            chat_messages.append(
                {
                    "role": role,
                    "content": content,
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
        attachments: list[Attachment] = [],
    ) -> BaseModel:

        prompt = self._build_prompt(
            messages,
            tool,
            attachments,
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
        ).to(self.model.device)

        for attempt in range(self.max_retries):

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                use_cache=True,
                temperature=self.temperature + attempt * 0.2,
                do_sample=(self.temperature + attempt * 0.2) > 0,
                pad_token_id=self.tokenizer.eos_token_id,
            )

            generated_tokens = outputs[
                0,
                inputs["input_ids"].shape[1]:,
            ]

            text = self.tokenizer.decode(
                generated_tokens,
                skip_special_tokens=True,
            )

            decision = self._parse_response(
                text,
                response_model,
            )

            # Valid output
            if decision.tool_calls or decision.response.strip():
                return decision

        print(
            f"Failed to generate a valid response after {self.max_retries} attempts."
        )

        return response_model(
            thought="Failed to generate a valid response.",
            response="Sorry, I couldn't answer this yet.",
            tool_calls=[],
        )
    

    def invoke_structured(
        self,
        messages,
        response_model: Type[BaseModel],
    ) -> BaseModel:
        """
        Invoke the model for structured generation without tool calling.

        Used for internal application tasks such as query rewriting,
        title generation, memory extraction, etc.
        """

        prompt = self.tokenizer.apply_chat_template(
            [
                {
                    "role": (
                        "system"
                        if msg.type == "system"
                        else "user"
                        if msg.type == "human"
                        else "assistant"
                    ),
                    "content": msg.content,
                }
                for msg in messages
            ],
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
        ).to(self.model.device)

        for _ in range(self.max_retries):

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                use_cache=True,
                temperature=self.temperature,
                do_sample=self.temperature > 0,
                pad_token_id=self.tokenizer.eos_token_id,
            )

            generated_tokens = outputs[
                0,
                inputs["input_ids"].shape[1]:,
            ]

            text = self.tokenizer.decode(
                generated_tokens,
                skip_special_tokens=True,
            )

            result = self._parse_response(
                text,
                response_model,
            )

            if result is not None:
                return result

        return response_model()