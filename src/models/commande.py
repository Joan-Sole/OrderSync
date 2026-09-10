from dataclasses import dataclass
from datetime import date
from models.lgcde import Lgcde


@dataclass
class Commande:
    TYPCDE: str
    NOCDE: str
    CFOUR: str
    CCOMPTE: str | None
    LIBCDE: str | None
    DTCDE: date
    HEURECDE: str
    NOCHRONO: str | None
    OBSER: str | None
    MODECDE: str
    DTLIVPREVU: date | None
    NBJOURS: str | None
    CDECENTRAL: bool | None
    TXREM: float | None
    MTCDE: float | None
    MTRECU: float | None
    MAGCDE: str
    MAGLIVR: str
    RETOUR_CDE: str | None
    DTREC: date | None
    DTFACT: date | None
    FORMAT_EDI: bool | None
    STATUTEDI: str | None

@dataclass
class Order:
    commande: Commande
    lines: list[Lgcde]