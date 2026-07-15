from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Lgcde:
    typcde: str
    nocde: str
    cmarq: str
    ccateg: str
    cprod: str
    qtecde: int
    qterecu: int
    paar: float
    mtlig: float