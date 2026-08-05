"""
UDP Atenciones, modelos
"""

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpAtencion(database.Model, UniversalMixin):
    """UdpAtencion"""

    # Nombre de la tabla
    __tablename__ = "udp_atenciones"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="udp_atenciones")
    udp_persona_id: Mapped[int] = mapped_column(ForeignKey("udp_personas.id"))
    udp_persona: Mapped["UdpPersona"] = relationship(back_populates="udp_atenciones")
    udp_tipo_tramite_id: Mapped[int] = mapped_column(ForeignKey("udp_tipos_tramites.id"))
    udp_tipo_tramite: Mapped["UdpTipoTramite"] = relationship(back_populates="udp_atenciones")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="udp_atenciones")

    # Columnas
    expediente: Mapped[Optional[str]] = mapped_column(String(32), default="", server_default="")
    observaciones: Mapped[Optional[str]] = mapped_column(String(1024), default="", server_default="")

    # Hijos: Solo se puede tener una contraparte por atención, por lo que se define una relación uno a uno
    udp_atencion_contraparte: Mapped[Optional["UdpAtencionContraparte"]] = relationship(back_populates="udp_atencion")

    def __repr__(self):
        """Representación"""
        return f"<UdpAtencion {self.id}>"
