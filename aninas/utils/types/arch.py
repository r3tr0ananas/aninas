from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

import udatetime

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Package:
    data: dict = field(default=None, repr=False)
    aur: bool = field(default=True, repr=False)

    repo: str = field(default=None)
    arch: str = field(default=None)
    description: str = field(default=None)
    last_update: datetime = field(default=None)
    out_of_date: bool = field(default=None)
    version: str = field(default=None)

    def __post_init__(self):
        if self.aur:
            self.description = self.data.get("Description")
            self.last_update = datetime.fromtimestamp(self.data.get("LastModified"))
            self.out_of_date = False if self.data.get("OutOfDate") is None else True
            self.version = self.data.get("Version")

            return

        self.repo = self.data.get("repo")
        self.arch = self.data.get("arch")
        self.description = self.data.get("description")
        self.last_update = udatetime.from_string(self.data.get("last_update"))
        self.out_of_date = self.data.get("outofdate", False)
        self.version = self.data.get("pkgver")
