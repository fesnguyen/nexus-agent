from app.tools.schemas import WebSearchInput
from app.tools.web_search import WebSearchTool

tool = WebSearchTool()

results = tool.run(
    WebSearchInput(
        query="Qwen3-VL"
    )
)

for result in results:
    print(result)
    print("=" * 80)