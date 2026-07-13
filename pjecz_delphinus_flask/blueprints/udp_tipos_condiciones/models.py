"""
UDP Tipos Condiciones, modelos
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpTipoCondicion(database.Model, UniversalMixin):
    """UdpTipoCondicion"""

    __tablename__ = "udp_tipos_condiciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(256), unique=True)
