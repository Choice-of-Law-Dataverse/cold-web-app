"""OpenAI spend tracking for eval runs.

Cost comes from Logfire: its OpenAI Agents instrumentation prices every model call
(`operation.cost`) and pydantic-evals sums that into each case's `cost` metric. This module
only keeps a running total so a run can stop starting new calls past a budget.
"""

from dataclasses import dataclass

import logfire
from agents import set_trace_processors

from app.config import config


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Budget:
    max_cost: float | None = None
    spent: float = 0.0
    unpriced_calls: int = 0

    def check(self) -> None:
        if self.max_cost is not None and self.spent >= self.max_cost:
            raise BudgetExceeded(f"Spent ${self.spent:.2f}, at the ${self.max_cost:.2f} budget; not starting new calls")


def configure_logfire() -> None:
    """Instrument like production so model calls are traced and priced; send only if a token is set."""
    logfire.configure(
        service_name="analyzer-evals",
        token=config.LOGFIRE_TOKEN,
        send_to_logfire="if-token-present",
        console=False,
    )
    logfire.instrument_openai_agents()
    # Logfire's instrumentation does not use the SDK's processors; dropping them stops exporting eval traces to OpenAI.
    set_trace_processors([])
