from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import os
import psutil

class Stats():
    def __init__(self) -> None:
        self.__process = psutil.Process(os.getpid())

        super().__init__()

    @property
    def cpu_usage(self) -> int:
        return self.__process.cpu_percent(0) / psutil.cpu_count()

    @property
    def ram_usage(self) -> int:
        return self.__convert_to_MB(self.__process.memory_info().rss)

    def __convert_to_MB(self, size):
        return (f"{size/float(1<<20):,.2f}")