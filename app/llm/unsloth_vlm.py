from pathlib import Path

from unsloth import FastVisionModel
from transformers import AutoProcessor

from app.agent.agent_state import AgentState
from app.agent.tool_call import ToolCall
from app.llm.base import BaseModel
from app.llm.generation_config import (
    DEFAULT_GENERATION_CONFIG,
)
from app.agent.tool_parser import (
    parse_tool_call,
)
from app.llm.prompt_builder import (
    PromptBuilder,
)


class UnslothVLM(BaseModel):
    """
    Qwen3-VL backend powered by Unsloth.

    Supports:
        - Text-only chat
        - Image + text chat
    """

    def __init__(
        self,
        model_name: str,
        max_seq_length: int = 4096,
    ) -> None:

        self.model_name = model_name

        print(
            f"Loading model: {model_name}"
        )

        self.model, self.tokenizer = (
            FastVisionModel.from_pretrained(
                model_name=model_name,
                max_seq_length=max_seq_length,
                load_in_4bit=True,
            )
        )

        FastVisionModel.for_inference(
            self.model
        )

        self.processor = AutoProcessor.from_pretrained(
            model_name,
            min_pixels=64 * 28 * 28,
            max_pixels=128 * 28 * 28,
            return_tensors="pt"
        )


    def generate_text(
        self,
        state: AgentState,
        image_path: str | None = None,
        tools: list[dict] | None = None,
    ) -> str:

        messages = PromptBuilder.build_messages(
                state
            )
        text = self.processor.apply_chat_template(
            messages,
            tools=tools,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.processor(
            text=[text],
            images=None,
            return_tensors="pt",
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            **DEFAULT_GENERATION_CONFIG,
        )

        # Remove prompt tokens and keep only model response.
        input_length = inputs["input_ids"].shape[1]

        generated_ids = outputs[:, input_length:]

        return self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]
    

    def generate_tool_call(
        self,
        state: AgentState,
        tools: list[dict],
        image_path: str | None = None,
    ) -> ToolCall | None:
        """
        Generate a tool call from a user request.

        Flow:
            User Request
                ↓
            Chat Messages
                ↓
            apply_chat_template(tools=...)
                ↓
            Model Generation
                ↓
            Decoded Response
                ↓
            Tool Call Extraction
                ↓
            ToolCall | None

        Returns:
            ToolCall:
                Model selected a tool.

            None:
                Model answered directly without
                requesting a tool.
        """
        if not state.system_prompt:
            state.system_prompt = """
Prioritize using tool to gather more information when user require new updates
"""

        messages = PromptBuilder.build_messages(
            state,
        )

        # Apply Qwen tool-calling template.
        text = self.processor.apply_chat_template(
            messages,
            tools=tools,
            tokenize=False,
            add_generation_prompt=True,
        )

        # Prepare model inputs.
        inputs = self.processor(
            text=[text],
            images=None,
            return_tensors="pt",
        ).to(self.model.device)

        # Generate model output.
        outputs = self.model.generate(
            **inputs,
            **DEFAULT_GENERATION_CONFIG,
        )

        # Decode generated tokens.
        input_length = inputs["input_ids"].shape[1]

        generated_ids = outputs[:, input_length:]

        response = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]

        # Parse native tool call.
        tool_call = parse_tool_call(response)

        # Return structured ToolCall.
        return tool_call