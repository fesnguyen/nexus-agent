# HumanMessage
```
from langchain_core.messages import HumanMessage

# Standardized object representing user/human input in a chat history.
# Helps LangChain seamlessly convert messages to any model format (OpenAI, Claude, Qwen).
user_prompt = HumanMessage(
    content="What is the current status?", 
    name="user_1"  # Optional: track multiple users or specific sub-agents
)

# Multimodal reminder: Pass structured blocks for images/files
image_prompt = HumanMessage(
    content=[
        {"type": "text", "text": "Analyze this chart:"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
    ]
)
```

# Pydantic
```
from typing import Literal, Optional
from pydantic import BaseModel, Field

# The industry standard to force structured outputs from LLMs (Structured Outputs).
# Guarantees the LLM returns a clean, typed Python object instead of messy raw text.
class AgentStep(BaseModel):
    # Field descriptions act as instructions directly read by the LLM!
    thought: str = Field(description="Internal reasoning loop before choosing an action.")
    action: Optional[Literal["search", "code_exec"]] = Field(None, description="Tool to run.")
    argument: Optional[str] = Field(None, description="The precise input argument for the tool.")

# LangChain Usage:
# structured_llm = llm.with_structured_output(AgentStep)
# response = structured_llm.invoke("Your prompt") -> returns an AgentStep object
```

# LangGraph State
```
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    # add_messages tells LangGraph to APPEND new HumanMessages/AIMessages 
    # to this list automatically instead of overwriting the conversation history.
    messages: Annotated[list[BaseMessage], add_messages]
```