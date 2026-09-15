    
# Location:  src\models

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
    DTCDE: str             # str "%Y%m%d" as date 
    HEURECDE: str | None
    NOCHRONO: str | None
    OBSER: str | None
    MODECDE: str | None
    DTLIVPREVU: str | None # str "%Y%m%d" as date 
    NBJOURS: str | None
    CDECENTRAL: bool | None
    TXREM: float | None
    MTCDE: float | None
    MTRECU: float | None
    MAGCDE: str | None
    MAGLIVR: str | None
    RETOUR_CDE: str | None
    DTREC: str | None      # str "%Y%m%d" as date 
    DTFACT: str | None     # str "%Y%m%d" as date 
    FORMAT_EDI: bool | None
    STATUTEDI: str | None

@dataclass
class Order:
    commande: Commande
    lines: list[Lgcde]