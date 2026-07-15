"""
Municipios, vistas
"""

import json

from flask import Blueprint, render_template, request, url_for
from flask_login import login_required

from pjecz_delphinus_flask.blueprints.estados.models import Estado
from pjecz_delphinus_flask.blueprints.municipios.models import Municipio
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_string

MODULO = "MUNICIPIOS"

municipios = Blueprint("municipios", __name__, template_folder="templates")


@municipios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@municipios.route("/municipios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Municipios"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = Municipio.query.join(Estado)
    if "estatus" in request.form:
        consulta = consulta.filter(Municipio.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(Municipio.estatus == "A")
    if "estado_id" in request.form:
        consulta = consulta.filter(Municipio.estado_id == request.form["estado_id"])
    if "clave" in request.form:
        clave = safe_string(request.form["clave"])
        if clave != "":
            consulta = consulta.filter(Municipio.clave.contains(clave))
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(Municipio.nombre.contains(nombre))
    registros = consulta.order_by(Estado.clave, Municipio.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "estado_nombre": resultado.estado.nombre,
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("municipios.detail", municipio_id=resultado.id),
                },
                "nombre": resultado.nombre,
            }
        )
    return output_datatable_json(draw, total, data)


@municipios.route("/municipios")
def list_active():
    """Listado de Municipios activos"""
    return render_template(
        "municipios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Municipios",
        estatus="A",
    )


@municipios.route("/municipios/<int:municipio_id>")
def detail(municipio_id):
    """Detalle de un Municipio"""
    municipio = Municipio.query.get_or_404(municipio_id)
    return render_template("municipios/detail.jinja2", municipio=municipio)


@municipios.route("/municipios/select_json", methods=["GET", "POST"])
def select_json():
    """Proporcionar el JSON con los ids, nombres para elegir con un select"""
    consulta = Municipio.query.filter(Municipio.estatus == "A")
    if "estado_id" in request.args:
        estado_id = request.args["estado_id"]
        consulta = consulta.filter(Municipio.estado_id == estado_id)
    consulta = consulta.order_by(Municipio.nombre).all()
    resultados = [{"id": m.id, "text": m.nombre} for m in consulta]
    return {"results": resultados, "pagination": {"more": False}}
