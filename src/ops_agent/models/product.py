from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from ops_agent.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    main_product_code: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    included_tonnage_quantity: Mapped[float] = mapped_column(Float, default=0.0)
