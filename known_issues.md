# Known issue when building nexus-agent

## Florence-2 Compatibility

### Problem

`microsoft/Florence-2-base` is incompatible with the current development environment (`transformers==5.5.0`).

### Evidence

During model initialization, multiple compatibility issues were encountered:

- `Florence2LanguageConfig` has no attribute `forced_bos_token_id`
- `RobertaTokenizer` has no attribute `additional_special_tokens`
- Additional missing dependencies (`einops`, `timm`)

These issues originate from Florence's remote implementation (`trust_remote_code=True`), not from the Nexus architecture.

### Conclusion

Instead of continuously patching Florence's source code, Nexus switched to another vision backend.

Because the vision pipeline is built around `BaseVisionWorker` and `VisionWorkerManager`, replacing the backend required only configuration changes without affecting the overall architecture.