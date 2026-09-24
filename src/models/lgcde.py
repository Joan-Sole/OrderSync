# Location:  src\models

from dataclasses import dataclass


@dataclass
class Lgcde:

	TYPCDE: str
	NOCDE: str
	CMARQ: str
	CCATEG: str
	CPROD: str
	PAAR: float | None
	PAMP: float | None
	QTESTK: int | None
	QTECDE: int | None
	TXREM: str | None
	TVA: float | None
	QTERECU: int | None
	QTEREFUS: int | None
	QTEFAC: int | None
	MTLIG: float | None

	@property
	def product_id(self) -> tuple[str, str, str]:
		"""
		Product identifier.
		"""
		return (
			self.CMARQ,
			self.CCATEG,
			self.CPROD,
		)


	@property
	def line_key(self) -> tuple[str, str, str, str]:
		"""
		Unique key of one order line.
		"""
		return (
			self.NOCDE,
			self.CMARQ,
			self.CCATEG,
			self.CPROD,
		)