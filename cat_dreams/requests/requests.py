from typing import Dict, List


class Request:
    def __init__(self, problem: str, required: List[str], forbidden: List[str] = None):
        self.problem = problem
        self.required = required

    def __repr__(self):
        return f"<Request: {self.problem}>"
