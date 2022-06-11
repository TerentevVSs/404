import datetime
import re
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    __name__: str
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now,
                        server_default=func.now())
    updated_at = Column(DateTime, default=datetime.datetime.now,
                        onupdate=datetime.datetime.now,
                        server_default=func.now())

    @declared_attr
    def __tablename__(cls) -> str:
        name_list = re.findall(f"[A-Z][a-z\d]*", cls.__name__)
        return "_".join(name_list).lower()
