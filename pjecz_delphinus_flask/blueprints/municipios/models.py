"""
Municipios, modelos
"""

from typing import List

from sqlalchemy import CHAR, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class Municipio(database.Model, UniversalMixin):
    """Municipio"""

    # Nombre de la tabla
    __tablename__ = "municipios"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Foránea
    estado_id: Mapped[int] = mapped_column(ForeignKey("estados.id"))
    estado = relationship("Estado", back_populates="municipios")

    # Columnas
    clave: Mapped[str] = mapped_column(CHAR(3))
    nombre: Mapped[str] = mapped_column(String(256))

    # Hijos
    udp_personas_domicilios: Mapped[List["UdpPersonaDomicilio"]] = relationship(back_populates="municipio")

    def __repr__(self):
        """Representación"""
        return f"<Estado {self.estado.clave} Municipio {self.clave}>"
