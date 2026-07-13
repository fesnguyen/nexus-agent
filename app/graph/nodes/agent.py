from app.core.app import agent_context
from app.graph.state import State
from app.graph.workers.agent_worker import (
    build_response_state,
    build_system_prompt,
    build_tool_state,
    invoke_model,
    persist_assistant_response,
    retrieve_contexts,
)
from app.prompt.system_prompts import SYSTEM_PROMPT
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

def agent_node(state: State):
    """
    This is the brain of the workflow:
    + Invoke model
    + Retrieve and attach memory/RAG
    + Build system prompt
    + Lead to tool/response
    """

    # Retrieval memory and rag context
    memory_context, retrieval_context = retrieve_contexts(
        state,
    )

    # System Prompt
    system_prompt = build_system_prompt(memory_context, retrieval_context)

    # Invoke Model
    decision = invoke_model(state, system_prompt)

    # If model decide to call a Tool
    if decision.tool_calls:
        return build_tool_state(decision, memory_context, retrieval_context)
    
    # Persist assistant response here since it's agent ownership
    persist_assistant_response(state, decision)

    # So no tool call => we have final answer now
    return build_response_state(decision)