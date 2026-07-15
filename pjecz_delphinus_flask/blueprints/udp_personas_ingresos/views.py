"""
UDP Personas Ingresos, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_personas.models import UdpPersona
from pjecz_delphinus_flask.blueprints.udp_personas_ingresos.forms import UdpPersonaIngresoForm
from pjecz_delphinus_flask.blueprints.udp_personas_ingresos.models import UdpPersonaIngreso
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_message, safe_string

MODULO = "UDP PERSONAS INGRESOS"

udp_personas_ingresos = Blueprint("udp_personas_ingresos", __name__, template_folder="templates")


@udp_personas_ingresos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_personas_ingresos.route("/udp_personas_ingresos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de UDP Personas Ingresos"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpPersonaIngreso.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "udp_persona_id" in request.form:
        consulta = consulta.filter(UdpPersonaIngreso.udp_persona_id == request.form["udp_persona_id"])
    registros = consulta.order_by(UdpPersonaIngreso.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("udp_personas_ingresos.detail", udp_persona_ingreso_id=resultado.id),
                },
                "ocupacion": resultado.ocupacion or "",
                "ingresos": str(resultado.ingresos) if resultado.ingresos else "",
            }
        )
    return output_datatable_json(draw, total, data)


@udp_personas_ingresos.route("/udp_personas_ingresos")
def list_active():
    """Listado de UDP Personas Ingresos activos"""
    return render_template(
        "udp_personas_ingresos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Ingresos",
        estatus="A",
    )


@udp_personas_ingresos.route("/udp_personas_ingresos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de UDP Personas Ingresos inactivos"""
    return render_template(
        "udp_personas_ingresos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Ingresos eliminados",
        estatus="B",
    )


@udp_personas_ingresos.route("/udp_personas_ingresos/<int:udp_persona_ingreso_id>")
def detail(udp_persona_ingreso_id):
    """Detalle de un UDP Persona Ingreso"""
    udp_persona_ingreso = UdpPersonaIngreso.query.get_or_404(udp_persona_ingreso_id)
    return render_template("udp_personas_ingresos/detail.jinja2", udp_persona_ingreso=udp_persona_ingreso)


@udp_personas_ingresos.route("/udp_personas_ingresos/nuevo/<int:udp_persona_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(udp_persona_id):
    """Nuevo UDP Persona Ingreso"""
    udp_persona = UdpPersona.query.get_or_404(udp_persona_id)
    form = UdpPersonaIngresoForm()
    if form.validate_on_submit():
        udp_persona_ingreso = UdpPersonaIngreso(
            udp_persona_id=udp_persona.id,
            ocupacion=safe_string(form.ocupacion.data, save_enie=True),
            ingresos=form.ingresos.data,
            observaciones=safe_string(form.observaciones.data, save_enie=True, max_len=1024),
        )
        udp_persona_ingreso.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo ingreso para {udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("udp_personas_ingresos/new.jinja2", form=form, udp_persona=udp_persona)


@udp_personas_ingresos.route("/udp_personas_ingresos/edicion/<int:udp_persona_ingreso_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_persona_ingreso_id):
    """Editar UDP Persona Ingreso"""
    udp_persona_ingreso = UdpPersonaIngreso.query.get_or_404(udp_persona_ingreso_id)
    form = UdpPersonaIngresoForm()
    if form.validate_on_submit():
        udp_persona_ingreso.ocupacion = safe_string(form.ocupacion.data, save_enie=True)
        udp_persona_ingreso.ingresos = form.ingresos.data
        udp_persona_ingreso.observaciones = safe_string(form.observaciones.data, save_enie=True, max_len=1024)
        udp_persona_ingreso.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado ingreso de {udp_persona_ingreso.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_ingreso.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.ocupacion.data = udp_persona_ingreso.ocupacion
    form.ingresos.data = udp_persona_ingreso.ingresos
    form.observaciones.data = udp_persona_ingreso.observaciones
    return render_template("udp_personas_ingresos/edit.jinja2", form=form, udp_persona_ingreso=udp_persona_ingreso)


@udp_personas_ingresos.route("/udp_personas_ingresos/eliminar/<int:udp_persona_ingreso_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_persona_ingreso_id):
    """Eliminar UDP Persona Ingreso"""
    udp_persona_ingreso = UdpPersonaIngreso.query.get_or_404(udp_persona_ingreso_id)
    if udp_persona_ingreso.estatus == "A":
        udp_persona_ingreso.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado ingreso de {udp_persona_ingreso.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_ingreso.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_ingreso.udp_persona_id))


@udp_personas_ingresos.route("/udp_personas_ingresos/recuperar/<int:udp_persona_ingreso_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_persona_ingreso_id):
    """Recuperar UDP Persona Ingreso"""
    udp_persona_ingreso = UdpPersonaIngreso.query.get_or_404(udp_persona_ingreso_id)
    if udp_persona_ingreso.estatus == "B":
        udp_persona_ingreso.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado ingreso de {udp_persona_ingreso.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_ingreso.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_ingreso.udp_persona_id))
