from app.core.infrastructure.unit_of_work import UnitOfWork


class BaseService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work
