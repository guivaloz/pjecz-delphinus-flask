"""
UDP Atenciones Contrapartes, vistas
"""

import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_atenciones_contrapartes.models import UdpAtencionContraparte
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json

MODULO = "UDP ATENCIONES CONTRAPARTES"

udp_atenciones_contrapartes = Blueprint("udp_atenciones_contrapartes", __name__, template_folder="templates")


@udp_atenciones_contrapartes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_atenciones_contrapartes.route("/udp_atenciones_contrapartes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Atenciones-Contrapartes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UdpAtencionContraparte.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "udp_atencion_id" in request.form:
        consulta = consulta.filter_by(udp_atencion_id=request.form["udp_atencion_id"])
    if "udp_contraparte_id" in request.form:
        consulta = consulta.filter_by(udp_contraparte_id=request.form["udp_contraparte_id"])
    # Ordenar y paginar
    registros = consulta.order_by(UdpAtencionContraparte.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("udp_atenciones_contrapartes.detail", udp_atencion_contraparte_id=resultado.id),
                },
                "udp_atencion_creado": {
                    "id": resultado.udp_atencion.id,
                    "creado": resultado.udp_atencion.creado.strftime("%Y-%m-%d %H:%M:%S"),
                    "url": url_for("udp_atenciones.detail", udp_atencion_id=resultado.udp_atencion.id),
                },
                "udp_atencion_autoridad_clave": resultado.udp_atencion.autoridad.clave,
                "udp_atencion_expediente": resultado.udp_atencion.expediente,
                "udp_atencion_tipo_tramite_nombre": resultado.udp_atencion.udp_tipo_tramite.nombre,
                "udp_contraparte_nombre_completo": {
                    "id": resultado.udp_contraparte.id,
                    "nombre_completo": resultado.udp_contraparte.nombre_completo,
                    "url": url_for("udp_contrapartes.detail", udp_contraparte_id=resultado.udp_contraparte.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@udp_atenciones_contrapartes.route("/udp_atenciones_contrapartes")
def list_active():
    """Listado de Atenciones-Contrapartes activas"""
    return render_template(
        "udp_atenciones_contrapartes/list.jinja2",
        estatus="A",
        filtros={"estatus": "A"},
        titulo="Atenciones-Contrapartes",
    )


@udp_atenciones_contrapartes.route("/udp_atenciones_contrapartes/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Atenciones-Contrapartes inactivas"""
    return render_template(
        "udp_atenciones_contrapartes/list.jinja2",
        estatus="B",
        filtros={"estatus": "B"},
        titulo="Atenciones-Contrapartes eliminadas",
    )


@udp_atenciones_contrapartes.route("/udp_atenciones_contrapartes/<int:udp_atencion_contraparte_id>")
def detail(udp_atencion_contraparte_id):
    """Detalle de una Atencion-Contraparte"""
    udp_atencion_contrapartes = UdpAtencionContraparte.query.get_or_404(udp_atencion_contraparte_id)
    return render_template("udp_atenciones_contrapartes/detail.jinja2", udp_atencion_contrapartes=udp_atencion_contrapartes)
