from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Commande:
    typcde: str
    nocde: str
    cfour: str
    ccompte: str
    libcde: str
    dtcde: Optional[date]
    heurecde: str
    mtcde: float
    mtrecu: float
    statutedi: str