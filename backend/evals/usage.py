"""OpenAI token and cost accounting for eval runs.

Installs an OpenAI client whose HTTP responses are inspected for `usage`, attributing tokens
to the step running in the current task. Prices come from a JSON file you maintain
(USD per million tokens), since they change: {"gpt-5.4-nano": {"input": 0.0, "output": 0.0}}.
"""

import json
from collections import defaultdict
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx2
import openai

from app.case_analyzer import config as analyzer_config
from app.config import config

current_step: ContextVar[str] = ContextVar("current_step", default="unattributed")
current_row: ContextVar["StepUsage | None"] = ContextVar("current_row", default=None)


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class StepUsage:
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    requests: int = 0
    unpriced_models: set[str] = field(default_factory=set)
    cost: float = 0.0


@dataclass
class UsageTracker:
    prices: dict[str, dict[str, float]]
    max_cost: float | None = None
    steps: dict[str, StepUsage] = field(default_factory=lambda: defaultdict(StepUsage))

    @property
    def total_cost(self) -> float:
        return sum(step.cost for step in self.steps.values())

    def record(self, model: str, usage: dict[str, Any]) -> None:
        for target in (self.steps[current_step.get()], current_row.get()):
            if target is not None:
                self._add(target, model, usage)

    def _add(self, step: StepUsage, model: str, usage: dict[str, Any]) -> None:
        input_tokens = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
        details = usage.get("input_tokens_details") or {}
        cached = int(details.get("cached_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or 0)
        step.input_tokens += input_tokens
        step.cached_input_tokens += cached
        step.output_tokens += output_tokens
        step.requests += 1

        price = self._price(model)
        if price is None:
            step.unpriced_models.add(model)
            return
        step.cost += (
            (input_tokens - cached) * price["input"]
            + cached * price.get("cached_input", price["input"])
            + output_tokens * price.get("output", 0.0)
        ) / 1_000_000

    def check_budget(self) -> None:
        if self.max_cost is not None and self.total_cost > self.max_cost:
            raise BudgetExceeded(f"Spent ${self.total_cost:.2f}, over the ${self.max_cost:.2f} budget")

    def _price(self, model: str) -> dict[str, float] | None:
        # Responses name dated snapshots (gpt-5.4-nano-2026-...); match the longest configured prefix.
        matches = [name for name in self.prices if model.startswith(name)]
        return self.prices[max(matches, key=len)] if matches else None


def load_prices(path: Path | None) -> dict[str, dict[str, float]]:
    return json.loads(path.read_text()) if path else {}


def install(tracker: UsageTracker) -> None:
    """Route the analyzer's OpenAI client through a usage-recording HTTP client."""

    async def on_response(response: httpx2.Response) -> None:
        if response.request.method != "POST" or response.status_code != 200:
            return
        await response.aread()
        try:
            body = json.loads(response.content)
        except ValueError:
            return
        if isinstance(body, dict) and isinstance(body.get("usage"), dict):
            tracker.record(str(body.get("model", "unknown")), body["usage"])

    analyzer_config._openai_client = openai.AsyncOpenAI(
        api_key=config.OPENAI_API_KEY,
        timeout=60.0,
        max_retries=3,
        http_client=httpx2.AsyncClient(timeout=60.0, event_hooks={"response": [on_response]}),
    )
