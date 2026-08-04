"""
UDP Contrapartes, modelos
"""

from datetime import date
from typing import Optional

from sqlalchemy import CHAR, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.universal_mixin import UniversalMixin


class UdpContraparte(database.Model, UniversalMixin):
    """UdpContraparte"""

    # Nombre de la tabla
    __tablename__ = "udp_contrapartes"
    __table_args__ = (Index("ix_udp_contrapartes_curp_no_vacio", "curp", unique=True, postgresql_where=text("curp != ''")),)

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    udp_sexo_id: Mapped[int] = mapped_column(ForeignKey("udp_sexos.id"))
    udp_sexo: Mapped["UdpSexo"] = relationship(back_populates="udp_contrapartes")

    # Columnas
    nombres: Mapped[str] = mapped_column(String(256))
    apellido_primero: Mapped[str] = mapped_column(String(256))
    apellido_segundo: Mapped[Optional[str]] = mapped_column(String(256), default="", server_default="")
    curp: Mapped[Optional[str]] = mapped_column(CHAR(18), default="", server_default="")
    nacimiento_fecha: Mapped[Optional[date]]
    observaciones: Mapped[Optional[str]] = mapped_column(String(1024), default="", server_default="")

    # Hijos
    udp_atenciones_contrapartes: Mapped[list["UdpAtencionContraparte"]] = relationship(back_populates="udp_contraparte")

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
        return f"<UdpContraparte {self.nombre_completo}>"
