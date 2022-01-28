from .IPipelineElement import IPipelineElement

from typing import List


class Gate:
    def __init__(self, name: str, pipeline: List[IPipelineElement]):
        self.name = name
        self.pipeline = pipeline
