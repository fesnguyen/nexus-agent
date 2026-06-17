# Phase 1 - Tool System

## Goal

Build the foundational tool layer for Nexus Agent.

The tool layer provides reusable capabilities that can be invoked by future agent workflows.

This phase intentionally excludes:

* RAG
* Memory
* Planning
* Vision
* Agent reasoning

The objective is to establish a clean and extensible tool architecture.

## Current Tool Execution Flow

User Input
    ↓
ToolRouter
    ↓
Selected Tool
    ↓
ToolArgumentExtractor
    ↓
JSON Arguments
    ↓
Pydantic Validation
    ↓
Tool Execution
    ↓
Result

---

# Architecture

```text
ToolRegistry
      │
      ├── CalculatorTool
      ├── FileReaderTool
      └── WebSearchTool
```

Each tool:

* Inherits from `BaseTool`
* Has a unique name
* Has a description
* Implements `run()`
* Uses Pydantic schemas for inputs

---

# Why ToolRegistry Exists

Without a registry:

```python
if tool_name == "calculator":
    ...
elif tool_name == "file_reader":
    ...
```

As the number of tools grows, this approach becomes difficult to maintain.

The registry centralizes tool discovery and retrieval.

Benefits:

* Decouples Agent from Tool implementations
* Simplifies tool registration
* Supports future dynamic tool loading

---

# CalculatorTool

## Responsibility

Perform safe arithmetic calculations.

## Example

```python
tool.run(
    CalculatorInput(
        expression="25 * 47"
    )
)
```

Expected Result:

```python
1175
```

---

# FileReaderTool

## Responsibility

Read local files from the workspace.

## Example

```python
tool.run(
    FileReaderInput(
        path="docs/roadmap.md"
    )
)
```

Expected Result:

```python
"# Nexus Agent Roadmap ..."
```

---

# WebSearchTool

## Responsibility

Search the web using SearXNG.

## Technologies

* SearXNG
* LangChain Community Tools

## Example

```python
tool.run(
    WebSearchInput(
        query="Latest Qwen3 release"
    )
)
```

Expected Result:

Relevant web search results.

---

# Design Principles

1. Single Responsibility

Each tool should perform one task.

2. Strong Typing

All tool inputs should be validated with Pydantic.

3. Testability

Every tool should be executable without the Agent.

4. Extensibility

Future tools should require minimal changes to existing code.

---

# Future Tools

Planned additions:

* RAGTool
* MemoryTool
* VisionTool
* CodeExecutionTool
* DatabaseTool
