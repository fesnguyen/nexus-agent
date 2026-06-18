from pydantic import BaseModel


class AgentState(BaseModel):
    """
    Current state of the agent.
    """

    user_input: str

    image_path: str | None = None

    observations: list[str] = []

    history: list[str] = []

    system_prompt: str | None = None