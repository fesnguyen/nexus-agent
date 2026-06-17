def parse_tool_name(
    response: str,
    valid_tools: list[str],
) -> str:

    response = response.strip().lower()

    for tool in valid_tools:
        if tool.lower() in response:
            return tool

    raise ValueError(
        f"Unable to parse tool: {response}"
    )