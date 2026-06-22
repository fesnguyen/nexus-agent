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

# TypeDict and Annotated
```
from typing import Annotated
from typing import TypedDict

# LangGraph standard for 3 reasons:
# 2. Easy to convert to JSON and vice versa
# 3. Functional Immutability, same state input and output every node can be easily modified without affecting other nodes.
# Here is now LangGraph handle state update:
# new_state = {**current_state, **node_output_dict}

class State(TypedDict, total=False):

    # 1. Dict syntax allows LangGraph to intercept this specific key and
    # automatically append new entries instead of overwriting the entire conversation array.
    messages: Annotated[list, add_messages]
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

# Architectures choosen
* Message-Centric Agent

    + Pros: Highly flexible, intuitive to design, and scales naturally with conversational history. Fits standard LLM instruction-following patterns out of the box.

    + Cons: Harder to control. Forcing complex logic (like retries or explicit branching) requires the model to parse long chat logs, increasing latency, VRAM footprint, and routing errors.

* State-Centric Agent

    + Pros: Deterministic and highly predictable control flow. Decouples graph routing from LLM outputs, simplifies tracking metadata (e.g., error counters), and saves tokens by keeping state fields isolated.

    + Cons: Higher initial architectural complexity. Requires explicit schemas, mapping logic to translate raw LLM outputs into variables, and meticulous state management.