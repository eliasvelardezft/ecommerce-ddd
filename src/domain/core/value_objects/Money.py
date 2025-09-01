from decimal import ROUND_HALF_UP, Decimal
from functools import total_ordering


@total_ordering
class Money:
    def __init__(self, amount: str | float | int | Decimal, currency: str):
        if currency is None or not isinstance(currency, str) or len(currency) != 3:
            raise ValueError("Currency must be a 3-letter string (e.g., 'USD')")
        self.currency = currency.upper()

        try:
            # For robust decimal conversion, especially from float
            self._amount = Decimal(str(amount))
        except Exception as e:
            raise ValueError(f"Invalid amount: {amount}. Must be convertible to Decimal.") from e

        # Standardize to 2 decimal places for most currencies, can be adjusted
        self._amount = self._amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


    @property
    def amount(self) -> Decimal:
        return self._amount

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot add Money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot subtract Money with different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | float | Decimal | str) -> "Money":
        if not isinstance(factor, (int, float, Decimal, str)):
            return NotImplemented
        try:
            factor_decimal = Decimal(str(factor))
        except Exception as e:
            raise ValueError(f"Invalid multiplication factor: {factor}. Must be numeric.") from e

        return Money(self.amount * factor_decimal, self.currency)

    def __truediv__(self, divisor: int | float | Decimal | str) -> "Money":
        if not isinstance(divisor, (int, float, Decimal, str)):
            return NotImplemented
        try:
            divisor_decimal = Decimal(str(divisor))
        except Exception as e:
            raise ValueError(f"Invalid division divisor: {divisor}. Must be numeric.") from e
        if divisor_decimal == Decimal(0):
            raise ValueError("Cannot divide Money by zero")
        return Money(self.amount / divisor_decimal, self.currency)

    # For Python 2 compatibility if needed, or explicit integer division
    def __div__(self, divisor: int | float | Decimal | str) -> "Money":
        return self.__truediv__(divisor)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot compare Money with different currencies")
        return self.amount < other.amount

    def __hash__(self):
        return hash((self._amount, self.currency))

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    # Allow multiplication with factor on the left: factor * Money(...)
    __rmul__ = __mul__

    def to_dict(self) -> dict:
        return {"amount": str(self.amount), "currency": self.currency}

    @classmethod
    def from_dict(cls, data: dict) -> "Money":
        return cls(amount=Decimal(data["amount"]), currency=data["currency"])

    @classmethod
    def zero(cls, currency: str) -> "Money":
        return cls(0, currency)

    def is_zero(self) -> bool:
        return self.amount == Decimal(0)

    def is_positive(self) -> bool:
        return self.amount > Decimal(0)

    def is_negative(self) -> bool:
        return self.amount < Decimal(0)
