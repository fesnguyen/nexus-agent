"""
Agent worker.

Contains the implementation details of the agent node.
"""

from __future__ import annotations

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from app.contracts.agent_decision import AgentDecision
from app.core.app import agent_context
from app.graph.state import State
from app.prompt.system_prompts import SYSTEM_PROMPT


def get_user_query(
    state: State,
) -> str:
    """
    Return the latest user query from the conversation.
    It's the lastest HumanMessage
    """

    for message in reversed(state["messages"]):

        if isinstance(message, HumanMessage):
            return message.content

    return ""


def retrieve_memory(
    user_query: str,
) -> str:
    """
    Retrieve relevant long-term memory.
    """

    return (
        agent_context.memory_manager
        .retrieve_context(
            query=user_query
        )
    )


def retrieve_rag(
    state: State,
    user_query: str,
) -> str:
    """
    Retrieve relevant knowledge from RAG.
    """

    history = [
        message.content
        for message in state["messages"]
        if isinstance(message, HumanMessage)
    ]

    return (
        agent_context.retrieval_service
        .retrieve(
            query=user_query,
            history=history,
        )
    )


def build_system_prompt(
    memory_context: str,
    retrieval_context: str,
) -> str:
    """
    Build the final system prompt.
    """

    context_parts = []

    if memory_context:
        context_parts.append(memory_context)

    if retrieval_context:
        context_parts.append(retrieval_context)

    prompt = SYSTEM_PROMPT

    if context_parts:

        prompt += (
            "\n\n"
            "Additional Context:\n"
            + "\n\n".join(context_parts)
        )

    return prompt


def invoke_model(
    state: State,
    system_prompt: str,
) -> AgentDecision:
    """
    Invoke the language model.
    """

    return agent_context.model.invoke(
        messages=[
            SystemMessage(
                content=system_prompt,
            ),
            *state["messages"],
        ],
        tool=agent_context.tool_registry,
    )


def build_tool_state(
    state: State,
    decision: AgentDecision,
):
    """
    Build the next graph state for tool execution.
    """

    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    tool.model_dump()
                    for tool in decision.tool_calls
                ],
            )
        ]
    }

def persist_assistant_response(state, decision):
    """
    Append message by conversation id as assistant response
    """
    if state['conversation_id']:
        agent_context.conversation_service.save_assistant_response(
            conversation_id=state["conversation_id"],
            response=decision.response,
        )

def build_response_state(
    decision: AgentDecision,
):
    """
    Build the next graph state for a final response.
    """

    return {
        "messages": [
            AIMessage(
                content=decision.response,
            )
        ]
    }