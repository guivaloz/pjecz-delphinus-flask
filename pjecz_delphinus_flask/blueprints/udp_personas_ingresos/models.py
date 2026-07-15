"""
UDP Personas Ingresos, modelos
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpPersonaIngreso(database.Model, UniversalMixin):
    """UdpPersonaIngreso"""

    # Nombre de la tabla
    __tablename__ = "udp_personas_ingresos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    udp_persona_id: Mapped[int] = mapped_column(ForeignKey("udp_personas.id"))
    udp_persona: Mapped["UdpPersona"] = relationship(back_populates="ingresos")

    # Columnas
    ocupacion: Mapped[Optional[str]] = mapped_column(String(256), default="", server_default="")
    ingresos: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=10, scale=2))
    observaciones: Mapped[Optional[str]] = mapped_column(String(1024), default="", server_default="")

    def __repr__(self):
        """Representación"""
        return f"<UdpPersonaIngreso {self.id}>"
