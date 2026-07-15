"""
UDP Personas Atenciones, modelos
"""

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpPersonaAtencion(database.Model, UniversalMixin):
    """UdpPersonaAtencion"""

    # Nombre de la tabla
    __tablename__ = "udp_personas_atenciones"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    udp_persona_id: Mapped[int] = mapped_column(ForeignKey("udp_personas.id"))
    udp_persona: Mapped["UdpPersona"] = relationship(back_populates="atenciones")
    udp_tipo_tramite_id: Mapped[int] = mapped_column(ForeignKey("udp_tipos_tramites.id"))
    udp_tipo_tramite: Mapped["UdpTipoTramite"] = relationship()
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship()
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship()

    # Columnas
    expediente: Mapped[Optional[str]] = mapped_column(String(32), default="", server_default="")
    observaciones: Mapped[Optional[str]] = mapped_column(String(1024), default="", server_default="")

    def __repr__(self):
        """Representación"""
        return f"<UdpPersonaAtencion {self.id}>"
