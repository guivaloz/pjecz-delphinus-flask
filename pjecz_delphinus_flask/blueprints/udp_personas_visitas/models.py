"""
UDP Personas Visitas, modelos
"""

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpPersonaVisita(database.Model, UniversalMixin):
    """UdpPersonaVisita"""

    # Nombre de la tabla
    __tablename__ = "udp_personas_visitas"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    udp_persona_id: Mapped[int] = mapped_column(ForeignKey("udp_personas.id"))
    udp_persona: Mapped["UdpPersona"] = relationship(back_populates="udp_personas_visitas")
    udp_tipo_visita_id: Mapped[int] = mapped_column(ForeignKey("udp_tipos_visitas.id"))
    udp_tipo_visita: Mapped["UdpTipoVisita"] = relationship(back_populates="udp_personas_visitas")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="udp_personas_visitas")

    # Columnas
    observaciones: Mapped[Optional[str]] = mapped_column(String(1024), default="", server_default="")

    def __repr__(self):
        """Representación"""
        return f"<UdpPersonaVisita {self.id}>"
