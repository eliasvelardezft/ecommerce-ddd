import re
from uuid import uuid4


class EntityId:
    """
    Value object for entity IDs that internally uses string representation of UUIDs
    but provides type safety and validation.
    """

    def __init__(self, value: str | None = None):
        if value is None:
            # Auto-generate UUID string
            self._value = str(uuid4())
        elif isinstance(value, str):
            # Validate that it's a valid UUID format
            self._validate_uuid_format(value)
            self._value = value
        else:
            raise ValueError(f"EntityId must be a string or None, got {type(value)}")

    @staticmethod
    def _validate_uuid_format(value: str) -> None:
        """Validate that the string is a valid UUID format"""
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
        )
        if not uuid_pattern.match(value):
            raise ValueError(f"Invalid UUID format: {value}")

    @classmethod
    def generate(cls) -> "EntityId":
        """Generate a new EntityId"""
        return cls()

    @classmethod
    def from_string(cls, value: str) -> "EntityId":
        """Create EntityId from existing string"""
        return cls(value)

    def __str__(self) -> str:
        """Return string representation (for database storage)"""
        return self._value

    def __repr__(self) -> str:
        return f"EntityId('{self._value}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, EntityId):
            return self._value == other._value
        elif isinstance(other, str):
            return self._value == other
        return False

    def __hash__(self) -> int:
        return hash(self._value)

    @property
    def value(self) -> str:
        """Get the string value (for explicit access)"""
        return self._value
