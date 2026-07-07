"""
Tareas, vistas
"""

import json

from flask import Blueprint, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.tareas.models import Tarea
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json

MODULO = "TAREAS"

tareas = Blueprint("tareas", __name__, template_folder="templates")


# @tareas.before_request
# @login_required
# @permission_required(MODULO, Permiso.VER)
# def before_request():
#     """Permiso por defecto"""


@tareas.route("/tareas/datatable_json", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.VER)
def datatable_json():
    """DataTable JSON para listado de Tareas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Tarea.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "comando" in request.form:
        consulta = consulta.filter_by(comando=request.form["comando"])
    if "usuario_id" in request.form:
        consulta = consulta.filter_by(usuario_id=request.form["usuario_id"])
    # Ordenar y paginar
    registros = consulta.order_by(Tarea.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "creado": resultado.creado.strftime("%Y-%m-%dT%H:%M:%S"),
                "detalle": {
                    "comando": resultado.comando,
                    "url": url_for("tareas.detail", tarea_id=resultado.id),
                },
                "ha_terminado": resultado.ha_terminado,
                "mensaje": resultado.mensaje,
                "usuario": {
                    "email": resultado.usuario.email,
                    "url": (
                        url_for("usuarios.detail", usuario_id=resultado.usuario_id) if current_user.can_view("USUARIOS") else ""
                    ),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@tareas.route("/tareas")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Tareas activos"""
    return render_template(
        "tareas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tareas",
        estatus="A",
    )


@tareas.route("/tareas/inactivos")
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Tareas inactivos"""
    return render_template(
        "tareas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Tareas inactivos",
        estatus="B",
    )


@tareas.route("/tareas/<tarea_id>")
@login_required
def detail(tarea_id):
    """Detalle de un Tarea"""
    tarea = Tarea.query.get_or_404(tarea_id)
    return render_template("tareas/detail.jinja2", tarea=tarea)
