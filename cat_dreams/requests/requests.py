from typing import List


class Request:
    def __init__(self, problem: str, required: List[str]):
        self.problem = problem
        self.required = required
