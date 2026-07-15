"""
UDP Personas Contrapartes, modelos
"""

from datetime import date
from typing import Optional

from sqlalchemy import CHAR, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpPersonaContraparte(database.Model, UniversalMixin):
    """UdpPersonaContraparte"""

    # Nombre de la tabla
    __tablename__ = "udp_personas_contrapartes"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    udp_persona_id: Mapped[int] = mapped_column(ForeignKey("udp_personas.id"))
    udp_persona: Mapped["UdpPersona"] = relationship(back_populates="contrapartes")

    # Columnas
    nombres: Mapped[str] = mapped_column(String(256))
    apellido_primero: Mapped[str] = mapped_column(String(256))
    apellido_segundo: Mapped[Optional[str]] = mapped_column(String(256), default="", server_default="")
    curp: Mapped[Optional[str]] = mapped_column(CHAR(18), default="", server_default="")
    nacimiento_fecha: Mapped[Optional[date]]
    observaciones: Mapped[Optional[str]] = mapped_column(String(1024), default="", server_default="")

    @property
    def nombre_completo(self):
        """Junta nombres, apellido primero y apellido segundo"""
        partes = [self.apellido_primero]
        if self.apellido_segundo:
            partes.append(self.apellido_segundo)
        partes.append(self.nombres)
        return " ".join(partes)

    def __repr__(self):
        """Representación"""
        return f"<UdpPersonaContraparte {self.nombre_completo}>"
