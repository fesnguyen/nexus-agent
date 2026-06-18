# Langgraph Overview

* 3 unique challenges associated with wrting applications that utilize LLMs: Latency, reliability and non-deterministic nature of LLM responses
  + Latency: LangGraph support parallelization task and Streaming generated tokens in real time to user
  + Reliability: Long-Running Agents can fail, which is expensive and time consuming: LangGraph provide checkpointing
  + The non deterministic nature of AI requires checkpoints, approvals, and testing: LangGraph provide Human-in-the-loop to collaborate with the user (Waiting for user to type), Tracing, Observation and Evaluation (LangSmith)

* LangGraph has 4 main components: 


## Requisites
Ensure you're using Python 3.11 - 3.13. This version is required for optimal compatibility with LangGraph

