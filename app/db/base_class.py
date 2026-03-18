from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: any
    __name__: str

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    @declared_attr
    def __tablename__(cls) -> str:  # pragma: no cover
        return cls.__name__.lower()
