from typing import TypedDict


class PlanningState(TypedDict, total=False):
    goal: str
    plan: list[str]
    current_step: int