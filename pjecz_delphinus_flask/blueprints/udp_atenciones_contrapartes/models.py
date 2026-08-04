"""
UDP Atenciones Contrapartes, modelos
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpAtencionContraparte(database.Model, UniversalMixin):
    """UdpAtencionContraparte"""

    # Nombre de la tabla
    __tablename__ = "udp_atenciones_contrapartes"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    udp_atencion_id: Mapped[int] = mapped_column(ForeignKey("udp_atenciones.id"), unique=True)
    udp_atencion: Mapped["UdpAtencion"] = relationship(back_populates="udp_atencion_contraparte")  # Solo una contraparte
    udp_contraparte_id: Mapped[int] = mapped_column(ForeignKey("udp_contrapartes.id"))
    udp_contraparte: Mapped["UdpContraparte"] = relationship(back_populates="udp_atenciones_contrapartes")

    def __repr__(self):
        """Representación"""
        return f"<UdpAtencionContraparte {self.id}>"
