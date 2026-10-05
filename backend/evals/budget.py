"""Model spend tracking for eval runs.

Cost comes from span attributes (`operation.cost`) that pydantic-evals sums into each case's
`cost` metric: Logfire's OpenAI Agents instrumentation prices every OpenAI call, and the Jev
client records the cost OpenRouter reports. Jev's judging of free-text answers runs in the
evaluators, outside any case, so its cost is kept apart from the steps'. This module only keeps
running totals so a run can stop starting new calls past a budget.
"""

from dataclasses import dataclass

import logfire
from agents import set_trace_processors

from app.config import config


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Budget:
    """New spend this run: spent by the steps, judge_spent by the judge; max_cost caps their sum."""

    max_cost: float | None = None
    spent: float = 0.0
    judge_spent: float = 0.0
    unpriced_calls: int = 0

    @property
    def total(self) -> float:
        return self.spent + self.judge_spent

    def check(self) -> None:
        if self.max_cost is not None and self.total >= self.max_cost:
            raise BudgetExceeded(f"Spent ${self.total:.2f}, at the ${self.max_cost:.2f} budget; not starting new calls")

    def add_judge_cost(self, cost: float | None) -> None:
        if cost is None:
            self.unpriced_calls += 1
        else:
            self.judge_spent += cost


def configure_logfire() -> None:
    """Instrument like production so model calls are traced and priced; send only if a token is set.

    Logfire's instrumentation does not use the Agents SDK's trace processors, so clearing them stops the SDK from
    exporting eval traces to OpenAI.
    """
    logfire.configure(
        service_name="analyzer-evals",
        token=config.LOGFIRE_TOKEN,
        send_to_logfire="if-token-present",
        console=False,
    )
    logfire.instrument_openai_agents()
    set_trace_processors([])
