from pathlib import Path

from app.agent.agent_state import AgentState
from pprint import pprint as ppr

class PromptBuilder:
    """
    Convert AgentState into model messages.
    Output Structure:

    [
        {
            "role": "system",
            "content": "<system_prompt>"
        },
        {
            "role": "user",
            "content": [

                # Optional image block.
                {
                    "type": "image",
                    "image": "<image_path>"
                },

                # Text block containing all agent context.
                {
                    "type": "text",
                    "text": '''
    User Request:
    ...

    Observations:
    ...

    History:
    ...
                }
            ]
        }
    ]

    Notes:
        - Image block is included only when an image exists.
        - User Request is always included.
        - System Prompt, Observations and History are included only when available.
    """

    @staticmethod
    def build_messages(
        state: AgentState,
    ) -> list[dict]:
        
        messages = []

        content = []

        sections = []

        # Append to sections
        sections.append(
            f"User Request:\n{state.user_input}"
        )
        if state.observations:

            sections.append(
                "Observations:\n"
                + "\n".join(
                    state.observations
                )
            )
        if state.history:

            sections.append(
                "History:\n"
                + "\n".join(
                    state.history
                )
            )

        # Append to content
        # Append image
        if state.image_path:
            image = Path(state.image_path)

            if not image.exists():
                raise FileNotFoundError(
                    state.image_path
                )
            
            content.append({
                "type": "image",
                "image": state.image_path
            })
        content.append(
            {
                "type": "text",
                "text": "\n\n".join(
                    sections
                ),
            }
        )

        # Append to messages
        if state.system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": state.system_prompt,
                }
            )
        messages.append(
            {
                "role": "user",
                "content": content,
            }
        )

        ppr(messages)

        return messages