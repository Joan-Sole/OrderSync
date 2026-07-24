from dataclasses import dataclass


@dataclass
class Lgcde:

	typcde: str
	nocde: str
	cmarq: str
	ccateg: str
	cprod: str

	paar: float
	pamp: float

	qtestk: int
	qtecde: int
	qterecu: int

	mtlig: float

	@property
	def product_id(self) -> tuple[str, str, str]:
		"""
		Product identifier.
		"""
		return (
			self.cmarq,
			self.ccateg,
			self.cprod,
		)


	@property
	def line_key(self) -> tuple[str, str, str, str]:
		"""
		Unique key of one order line.
		"""
		return (
			self.nocde,
			self.cmarq,
			self.ccateg,
			self.cprod,
		)