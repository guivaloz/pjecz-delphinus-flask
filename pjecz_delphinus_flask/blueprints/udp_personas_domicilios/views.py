"""
UDP Personas Domicilios, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_personas.models import UdpPersona
from pjecz_delphinus_flask.blueprints.udp_personas_domicilios.forms import UdpPersonaDomicilioForm
from pjecz_delphinus_flask.blueprints.udp_personas_domicilios.models import UdpPersonaDomicilio
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_message, safe_string

MODULO = "UDP PERSONAS DOMICILIOS"

udp_personas_domicilios = Blueprint("udp_personas_domicilios", __name__, template_folder="templates")


@udp_personas_domicilios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_personas_domicilios.route("/udp_personas_domicilios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de UDP Personas Domicilios"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpPersonaDomicilio.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "udp_persona_id" in request.form:
        consulta = consulta.filter(UdpPersonaDomicilio.udp_persona_id == request.form["udp_persona_id"])
    registros = consulta.order_by(UdpPersonaDomicilio.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("udp_personas_domicilios.detail", udp_persona_domicilio_id=resultado.id),
                },
                "calle": resultado.calle or "",
                "num_exterior": resultado.num_exterior or "",
                "colonia": resultado.colonia or "",
                "municipio_nombre": resultado.municipio.nombre,
            }
        )
    return output_datatable_json(draw, total, data)


@udp_personas_domicilios.route("/udp_personas_domicilios")
def list_active():
    """Listado de UDP Personas Domicilios activos"""
    return render_template(
        "udp_personas_domicilios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="UDP Personas Domicilios",
        estatus="A",
    )


@udp_personas_domicilios.route("/udp_personas_domicilios/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de UDP Personas Domicilios inactivos"""
    return render_template(
        "udp_personas_domicilios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="UDP Personas Domicilios inactivos",
        estatus="B",
    )


@udp_personas_domicilios.route("/udp_personas_domicilios/<int:udp_persona_domicilio_id>")
def detail(udp_persona_domicilio_id):
    """Detalle de un UDP Persona Domicilio"""
    udp_persona_domicilio = UdpPersonaDomicilio.query.get_or_404(udp_persona_domicilio_id)
    return render_template("udp_personas_domicilios/detail.jinja2", udp_persona_domicilio=udp_persona_domicilio)


@udp_personas_domicilios.route("/udp_personas_domicilios/nuevo/<int:udp_persona_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(udp_persona_id):
    """Nuevo UDP Persona Domicilio"""
    udp_persona = UdpPersona.query.get_or_404(udp_persona_id)
    form = UdpPersonaDomicilioForm()
    if form.validate_on_submit():
        udp_persona_domicilio = UdpPersonaDomicilio(
            udp_persona_id=udp_persona.id,
            municipio_id=form.municipio.data,
            calle=safe_string(form.calle.data, save_enie=True),
            num_exterior=safe_string(form.num_exterior.data),
            num_interior=safe_string(form.num_interior.data),
            colonia=safe_string(form.colonia.data, save_enie=True),
            codigo_postal=form.codigo_postal.data,
            referencias=safe_string(form.referencias.data, save_enie=True, max_len=1024),
        )
        udp_persona_domicilio.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo domicilio para {udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("udp_personas_domicilios/new.jinja2", form=form, udp_persona=udp_persona)


@udp_personas_domicilios.route("/udp_personas_domicilios/edicion/<int:udp_persona_domicilio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_persona_domicilio_id):
    """Editar UDP Persona Domicilio"""
    udp_persona_domicilio = UdpPersonaDomicilio.query.get_or_404(udp_persona_domicilio_id)
    form = UdpPersonaDomicilioForm()
    if form.validate_on_submit():
        udp_persona_domicilio.municipio_id = form.municipio.data
        udp_persona_domicilio.calle = safe_string(form.calle.data, save_enie=True)
        udp_persona_domicilio.num_exterior = safe_string(form.num_exterior.data)
        udp_persona_domicilio.num_interior = safe_string(form.num_interior.data)
        udp_persona_domicilio.colonia = safe_string(form.colonia.data, save_enie=True)
        udp_persona_domicilio.codigo_postal = form.codigo_postal.data
        udp_persona_domicilio.referencias = safe_string(form.referencias.data, save_enie=True, max_len=1024)
        udp_persona_domicilio.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado domicilio de {udp_persona_domicilio.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_domicilio.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.municipio.data = udp_persona_domicilio.municipio_id
    form.calle.data = udp_persona_domicilio.calle
    form.num_exterior.data = udp_persona_domicilio.num_exterior
    form.num_interior.data = udp_persona_domicilio.num_interior
    form.colonia.data = udp_persona_domicilio.colonia
    form.codigo_postal.data = udp_persona_domicilio.codigo_postal
    form.referencias.data = udp_persona_domicilio.referencias
    return render_template("udp_personas_domicilios/edit.jinja2", form=form, udp_persona_domicilio=udp_persona_domicilio)


@udp_personas_domicilios.route("/udp_personas_domicilios/eliminar/<int:udp_persona_domicilio_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_persona_domicilio_id):
    """Eliminar UDP Persona Domicilio"""
    udp_persona_domicilio = UdpPersonaDomicilio.query.get_or_404(udp_persona_domicilio_id)
    if udp_persona_domicilio.estatus == "A":
        udp_persona_domicilio.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado domicilio de {udp_persona_domicilio.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_domicilio.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_domicilio.udp_persona_id))


@udp_personas_domicilios.route("/udp_personas_domicilios/recuperar/<int:udp_persona_domicilio_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_persona_domicilio_id):
    """Recuperar UDP Persona Domicilio"""
    udp_persona_domicilio = UdpPersonaDomicilio.query.get_or_404(udp_persona_domicilio_id)
    if udp_persona_domicilio.estatus == "B":
        udp_persona_domicilio.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado domicilio de {udp_persona_domicilio.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_domicilio.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_domicilio.udp_persona_id))
