"""
Estados, modelos
"""

from sqlalchemy import CHAR, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class Estado(database.Model, UniversalMixin):
    """Estado"""

    # Nombre de la tabla
    __tablename__ = "estados"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    clave: Mapped[str] = mapped_column(CHAR(2), unique=True)
    nombre: Mapped[str] = mapped_column(String(256))

    # Hijos
    municipios = relationship("Municipio", back_populates="estado")

    def __repr__(self):
        """Representación"""
        return f"<Estado {self.nombre}>"
