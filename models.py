from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): #Creating our Base model that all other models will inherit from
    pass

db = SQLAlchemy(model_class=Base)

class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(db.String(255))
    order: Mapped[str] = mapped_column(db.String(255))

