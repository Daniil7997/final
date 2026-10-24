from sqlalchemy import CheckConstraint


def range_1_to_5(table_name: str,
                 column_name: str,
                 constr_name: str | None = None) -> CheckConstraint:
    """Generates a DB constraint for the range 1 to 5 with a unique name."""
    return CheckConstraint(
        f"{column_name} >= 1 AND {column_name} <= 5",
        name=constr_name or f"chk_{table_name}_{column_name}_1_to_5"
    )
