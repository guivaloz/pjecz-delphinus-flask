"""
UDP Tipos Tramites, modelos
"""

from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpTipoTramite(database.Model, UniversalMixin):
    """UdpTipoTramite"""

    # Nombre de la tabla
    __tablename__ = "udp_tipos_tramites"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[str] = mapped_column(String(256), unique=True)

    # Hijos
    udp_personas_atenciones: Mapped[List["UdpPersonaAtencion"]] = relationship(back_populates="udp_tipo_tramite")

    def __repr__(self):
        """Representación"""
        return f"<UdpTipoTramite {self.nombre}>"
