from langchain_core.messages import AIMessage
from pprint import pprint as ppr

ai_message = AIMessage(
    content="Hello world!",
) 

ppr(ai_message)