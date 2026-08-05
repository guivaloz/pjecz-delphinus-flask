"""
UDP Domicilios, vistas
"""

import json

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.estados.models import Estado
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.municipios.models import Municipio
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_domicilios.forms import UdpDomicilioForm
from pjecz_delphinus_flask.blueprints.udp_domicilios.models import UdpDomicilio
from pjecz_delphinus_flask.blueprints.udp_personas.models import UdpPersona
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_message, safe_string

MODULO = "UDP DOMICILIOS"

udp_domicilios = Blueprint("udp_domicilios", __name__, template_folder="templates")


@udp_domicilios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_domicilios.route("/udp_domicilios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Domicilios"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpDomicilio.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "udp_persona_id" in request.form:
        consulta = consulta.filter(UdpDomicilio.udp_persona_id == request.form["udp_persona_id"])
    registros = consulta.order_by(UdpDomicilio.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "calle": resultado.calle,
                    "url": url_for("udp_domicilios.detail", udp_domicilio_id=resultado.id),
                },
                "num_exterior": resultado.num_exterior,
                "num_interior": resultado.num_interior,
                "colonia": resultado.colonia,
                "municipio_nombre": resultado.municipio.nombre,
            }
        )
    return output_datatable_json(draw, total, data)


@udp_domicilios.route("/udp_domicilios")
def list_active():
    """Listado de Domicilios activos"""
    return render_template(
        "udp_domicilios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Domicilios",
        estatus="A",
    )


@udp_domicilios.route("/udp_domicilios/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Domicilios inactivos"""
    return render_template(
        "udp_domicilios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Domicilios eliminados",
        estatus="B",
    )


@udp_domicilios.route("/udp_domicilios/<int:udp_domicilio_id>")
def detail(udp_domicilio_id):
    """Detalle de un Domicilio"""
    udp_domicilio = UdpDomicilio.query.get_or_404(udp_domicilio_id)
    return render_template("udp_domicilios/detail.jinja2", udp_domicilio=udp_domicilio)


@udp_domicilios.route("/udp_domicilios/nuevo/<int:udp_persona_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(udp_persona_id):
    """Nuevo Domicilio"""
    udp_persona = UdpPersona.query.get_or_404(udp_persona_id)
    form = UdpDomicilioForm()
    if form.validate_on_submit():
        udp_domicilio = UdpDomicilio(
            udp_persona_id=udp_persona.id,
            municipio_id=form.municipio.data,
            calle=safe_string(form.calle.data, save_enie=True),
            num_exterior=safe_string(form.num_exterior.data),
            num_interior=safe_string(form.num_interior.data),
            colonia=safe_string(form.colonia.data, save_enie=True),
            codigo_postal=form.codigo_postal.data,
            referencias=safe_string(form.referencias.data, save_enie=True, max_len=1024),
        )
        udp_domicilio.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo domicilio para {udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    estado_por_defecto = Estado.query.filter_by(clave=current_app.config["ESTADO_CLAVE"]).first()
    if estado_por_defecto:
        municipio_por_defecto = Municipio.query.filter_by(
            estado_id=estado_por_defecto.id, clave=current_app.config["MUNICIPIO_CLAVE"]
        ).first()
    else:
        municipio_por_defecto = None
    return render_template(
        "udp_domicilios/new.jinja2",
        form=form,
        udp_persona=udp_persona,
        estado_por_defecto=estado_por_defecto,
        municipio_por_defecto=municipio_por_defecto,
    )


@udp_domicilios.route("/udp_domicilios/edicion/<int:udp_domicilio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_domicilio_id):
    """Editar Domicilio"""
    udp_domicilio = UdpDomicilio.query.get_or_404(udp_domicilio_id)
    form = UdpDomicilioForm()
    if form.validate_on_submit():
        udp_domicilio.municipio_id = form.municipio.data
        udp_domicilio.calle = safe_string(form.calle.data, save_enie=True)
        udp_domicilio.num_exterior = safe_string(form.num_exterior.data)
        udp_domicilio.num_interior = safe_string(form.num_interior.data)
        udp_domicilio.colonia = safe_string(form.colonia.data, save_enie=True)
        udp_domicilio.codigo_postal = form.codigo_postal.data
        udp_domicilio.referencias = safe_string(form.referencias.data, save_enie=True, max_len=1024)
        udp_domicilio.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado domicilio de {udp_domicilio.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_domicilio.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.municipio.data = udp_domicilio.municipio_id
    form.calle.data = udp_domicilio.calle
    form.num_exterior.data = udp_domicilio.num_exterior
    form.num_interior.data = udp_domicilio.num_interior
    form.colonia.data = udp_domicilio.colonia
    form.codigo_postal.data = udp_domicilio.codigo_postal
    form.referencias.data = udp_domicilio.referencias
    return render_template("udp_domicilios/edit.jinja2", form=form, udp_domicilio=udp_domicilio)


@udp_domicilios.route("/udp_domicilios/eliminar/<int:udp_domicilio_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_domicilio_id):
    """Eliminar Domicilio"""
    udp_domicilio = UdpDomicilio.query.get_or_404(udp_domicilio_id)
    if udp_domicilio.estatus == "A":
        udp_domicilio.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado domicilio de {udp_domicilio.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_domicilio.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_domicilio.udp_persona_id))


@udp_domicilios.route("/udp_domicilios/recuperar/<int:udp_domicilio_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_domicilio_id):
    """Recuperar Domicilio"""
    udp_domicilio = UdpDomicilio.query.get_or_404(udp_domicilio_id)
    if udp_domicilio.estatus == "B":
        udp_domicilio.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado domicilio de {udp_domicilio.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_domicilio.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_domicilio.udp_persona_id))
