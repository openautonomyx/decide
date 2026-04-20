from dataclasses import dataclass


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str | None = None


class BasePolicy:
    def evaluate(self, user_input: str) -> PolicyDecision:
        return PolicyDecision(allowed=True)


class InputLengthPolicy(BasePolicy):
    def __init__(self, max_chars: int) -> None:
        self.max_chars = max_chars

    def evaluate(self, user_input: str) -> PolicyDecision:
        if len(user_input) > self.max_chars:
            return PolicyDecision(False, f"Input exceeds max size {self.max_chars}")
        return PolicyDecision(True)
