from app.core.app import container
from app.graph.state import State
from app.prompt.system_prompts import SYSTEM_PROMPT
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

def agent_node(state: State):

    #
    # Latest user query
    #
    user_query = ""

    for message in reversed(state["messages"]):

        if isinstance(message, HumanMessage):

            user_query = message.content

            break

    memory_context = (
        container.memory_manager
        .retrieve_context(
            query=user_query
        )
    )

    #
    # Retrieval Context
    #
    retrieval_context = (
        container.retrieval_service
        .retrieve(
            query=user_query,
        )
    )

    #
    # Build Context
    #
    context_parts = []

    if memory_context:

        context_parts.append(
            memory_context
        )

    if retrieval_context:

        context_parts.append(
            retrieval_context
        )

    context = "\n\n".join(
        context_parts
    )

    #
    # System Prompt
    #
    system_prompt = SYSTEM_PROMPT

    if context:

        system_prompt += (
            "\n\n"
            "Additional Context:\n"
            f"{context}"
        )


    #
    # Invoke Model
    #
    decision = container.model.invoke(
        messages=[
            # Always put System Message to the top of the conversation
            SystemMessage(
                content=system_prompt,
            ),
            *state["messages"],
        ],
        tool=container.tool_registry,
    )

    #
    # Tool call
    #
    if decision.tool_calls:

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

    #
    # Final answer
    #
    return {
        "messages": [
            AIMessage(
                content=decision.response
            )
        ]
    }