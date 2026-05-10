from typing import Dict, List


class Request:
    def __init__(self, name: str, problem: str, required: List[str], forbidden: List[str] = None):
        self.name = name
        self.problem = problem
        self.required = required
        self.forbidden = forbidden

    def __repr__(self):
        return f"<Request: {self.name}>"
