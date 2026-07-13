"""
UDP Tipos Visitas, modelos
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpTipoVisita(database.Model, UniversalMixin):
    """UdpTipoVisita"""

    __tablename__ = "udp_tipos_visitas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(256), unique=True)
