from enum import StrEnum


"""
exception codes
https://www.postgresql.org/docs/current/errcodes-appendix.html
"""


class DBIntegrityState(StrEnum):
    """
    Class 23: Violation of data integrity constraints
    """
    # Violation of the prohibition on deletion or alteration.
    RESTRICT_VIOLATION = "23001"
    # Attempt to write NULL to a field with nullable=False
    NOT_NULL_VIOLATION = "23502"
    # Link to a non-existent ID
    FOREIGN_KEY_VIOLATION = "23503"
    # Duplicate of a unique field / PK
    UNIQUE_VIOLATION = "23505"
    # Violation of a custom CheckConstraint
    CHECK_VIOLATION = "23514"
    # EXCLUDE (Exclusion Constraint) violation
    EXCLUSION_VIOLATION = "23P01"
