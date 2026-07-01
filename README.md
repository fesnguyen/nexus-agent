# nexus-agent
Agentic RAG assistant powered by local LLMs.

# ERROR: 
## WARNING:  WatchFiles detected changes in 'unsloth_compiled_cache/moe_utils.py'. Reloading...
* Solution: 
  + Best:
    ```
    uvicorn.run(
      ...
      reload=True,
      reload_excludes=["unsloth_compiled_cache/*"],
    )
    ```
  + Run: uvicorn main:app --reload --reload-exclude "unsloth_compiled_cache/*"