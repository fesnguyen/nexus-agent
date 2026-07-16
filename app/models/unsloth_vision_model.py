import json
import re
from typing import Type

from PIL import Image
from pydantic import BaseModel
import torch
from transformers import AutoProcessor
from unsloth import FastVisionModel

from app.contracts.agent_decision import AgentDecision
from app.models.base import BaseLLM
from app.tools.registry import ToolRegistry
from langchain_core.messages import HumanMessage


class UnslothVisionModel(BaseLLM):

    def __init__(
        self,
        model_name: str,
        **kwargs,
    ):
        self.model_name = model_name
        self.max_new_tokens = kwargs.get("max_new_tokens", 128)
        self.max_seq_length = kwargs.get(
            "max_seq_length",
            self.max_new_tokens * 8,
        )
        self.min_pixels = kwargs.get("min_pixels", 32 * 28 * 28)
        self.max_pixels = kwargs.get("max_pixels", 64 * 28 * 28)
        self.temperature = kwargs.get("temperature", 0.0)

        print(f"Loading vision model: {model_name}")

        self.model, _ = FastVisionModel.from_pretrained(
            model_name=model_name,
            max_seq_length=self.max_seq_length,
            dtype=None,
            load_in_4bit=True,
            device_map="cuda",
        )

        self.processor = AutoProcessor.from_pretrained(
            model_name,
            min_pixels=self.min_pixels,
            max_pixels=self.max_pixels,
            return_tensors="pt",
            model_max_length=self.max_seq_length
        )

        FastVisionModel.for_inference(self.model)

    def _build_messages(self, messages):
        chat_messages = []
        extracted_images = []

        for msg in messages:
            if msg.type == "system":
                role = "system"
            elif msg.type == "ai":
                role = "assistant"
            elif msg.type == "tool":
                role = "tool"
            else:
                role = "user"

            text_content = ""
            # If the content is a uniform VLM list structure (primarily user messages)
            if isinstance(msg.content, list):
                user_message_content = []
                for item in msg.content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            user_message_content.append({
                                "type": "text", 
                                "text": item.get("text", "")
                            })
                        elif item.get("type") == "image_url":
                            img_source = item["image_url"].get("url")
                            extracted_images.append(img_source)
                            
                            # Append the structural image dictionary block to line up with the processor array
                            user_message_content.append({
                                "type": "image"
                            })
                
                chat_messages.append({
                    "role": role,
                    "content": user_message_content
                })
            else:
                chat_messages.append({
                    "role": role,
                    "content": msg.content if msg.content else "",
                })

        return chat_messages, extracted_images

    def _parse_response(
        self,
        text: str,
        response_model: Type[BaseModel],
    ) -> BaseModel | None:
        try:
            match = re.search(
                r"\{.*\}",
                text,
                re.DOTALL,
            )

            if match:
                text = match.group(0)

            data = json.loads(text)

            return response_model.model_validate(data)
        except Exception as e:
            print(f"Failed to parse model output, exception: {e}")
            return None

    def invoke(
        self,
        messages,
        tool: ToolRegistry,
        response_model: Type[BaseModel] = AgentDecision,
    ) -> BaseModel:
        # Format the historical conversation and extract any attached multimodal image components
        chat_messages, images = self._build_messages(messages)
        # Apply the structured chat template with tools schema formatting to compile the raw text prompt
        text = self.processor.apply_chat_template(
            chat_messages,
            tools=tool.get_tool_schemas(),
            add_generation_prompt=True,
            tokenize=False,
        )

        # VLM processor process the image and text
        processing_args = {"text": text, "return_tensors": "pt"}
        if images:
            processing_args["images"] = images
        inputs = self.processor(**processing_args).to(self.model.device)

        # Initialize response tracking variables
        response = None
        max_iterations = 3
        self.temperature = 0
        for iteration in range(max_iterations):
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                use_cache=True,
                temperature=self.temperature,
                do_sample=self.temperature > 0,
                pad_token_id=self.processor.tokenizer.eos_token_id,
            )

            # Slice the sequence to isolate newly predicted response tokens
            generated_tokens = outputs[
                0,
                inputs["input_ids"].shape[1] :,
            ]

            # Decode token stream back into human-readable text
            text = self.processor.decode(
                generated_tokens,
                skip_special_tokens=True,
            )

            print(f"Attempt {iteration}: {text}")

            # Attempt to validate and parse text into your expected response schema
            response = self._parse_response(
                text,
                response_model,
            )

            # If successfully parsed, break the loop early and proceed
            if response is not None:
                break
                
            print(f"Parsing failed on iteration {iteration + 1}/{max_iterations}. Retrying...")
            self.temperature += 0.5

        # Optional: Raise an explicit error or handle fallback logic if all 3 attempts returned None
        if response is None:
            raise ValueError(f"Failed to generate a valid structured response after {max_iterations} attempts.")

        return response