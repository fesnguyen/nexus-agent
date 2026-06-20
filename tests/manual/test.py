from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage

hm = HumanMessage("What is LoRA")
print(hm)

# Test more langchain core message types
sm = SystemMessage(content="This is a system message.")
print(sm)
