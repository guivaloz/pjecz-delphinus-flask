"""
UDP Tipos Visitas, modelos
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpTipoVisita(database.Model, UniversalMixin):
    """UdpTipoVisita"""

    # Nombre de la tabla
    __tablename__ = "udp_tipos_visitas"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[str] = mapped_column(String(256), unique=True)

    def __repr__(self):
        """Representación"""
        return f"<UdpTipoVisita {self.nombre}>"
