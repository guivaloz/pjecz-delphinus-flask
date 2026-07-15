"""
UDP Personas Domicilios, modelos
"""

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpPersonaDomicilio(database.Model, UniversalMixin):
    """UdpPersonaDomicilio"""

    # Nombre de la tabla
    __tablename__ = "udp_personas_domicilios"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    udp_persona_id: Mapped[int] = mapped_column(ForeignKey("udp_personas.id"))
    udp_persona: Mapped["UdpPersona"] = relationship(back_populates="domicilios")
    municipio_id: Mapped[int] = mapped_column(ForeignKey("municipios.id"))
    municipio: Mapped["Municipio"] = relationship()

    # Columnas
    calle: Mapped[Optional[str]] = mapped_column(String(256), default="", server_default="")
    num_exterior: Mapped[Optional[str]] = mapped_column(String(64), default="", server_default="")
    num_interior: Mapped[Optional[str]] = mapped_column(String(64), default="", server_default="")
    colonia: Mapped[Optional[str]] = mapped_column(String(256), default="", server_default="")
    codigo_postal: Mapped[Optional[int]]
    referencias: Mapped[Optional[str]] = mapped_column(String(1024), default="", server_default="")

    def __repr__(self):
        """Representación"""
        return f"<UdpPersonaDomicilio {self.id}>"
