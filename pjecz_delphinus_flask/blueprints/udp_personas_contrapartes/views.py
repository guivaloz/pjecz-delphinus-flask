"""
UDP Personas Contrapartes, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_personas.models import UdpPersona
from pjecz_delphinus_flask.blueprints.udp_personas_contrapartes.forms import UdpPersonaContraparteForm
from pjecz_delphinus_flask.blueprints.udp_personas_contrapartes.models import UdpPersonaContraparte
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_message, safe_string

MODULO = "UDP PERSONAS CONTRAPARTES"

udp_personas_contrapartes = Blueprint("udp_personas_contrapartes", __name__, template_folder="templates")


@udp_personas_contrapartes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_personas_contrapartes.route("/udp_personas_contrapartes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de UDP Personas Contrapartes"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpPersonaContraparte.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "udp_persona_id" in request.form:
        consulta = consulta.filter(UdpPersonaContraparte.udp_persona_id == request.form["udp_persona_id"])
    if "nombres" in request.form:
        nombres = safe_string(request.form["nombres"], save_enie=True)
        if nombres != "":
            consulta = consulta.filter(UdpPersonaContraparte.nombres.contains(nombres))
    if "apellido_primero" in request.form:
        apellido_primero = safe_string(request.form["apellido_primero"], save_enie=True)
        if apellido_primero != "":
            consulta = consulta.filter(UdpPersonaContraparte.apellido_primero.contains(apellido_primero))
    registros = (
        consulta.order_by(
            UdpPersonaContraparte.apellido_primero, UdpPersonaContraparte.apellido_segundo, UdpPersonaContraparte.nombres
        )
        .offset(start)
        .limit(rows_per_page)
        .all()
    )
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre_completo": resultado.nombre_completo,
                    "url": url_for("udp_personas_contrapartes.detail", udp_persona_contraparte_id=resultado.id),
                },
                "curp": resultado.curp or "",
                "nacimiento_fecha": resultado.nacimiento_fecha.strftime("%Y-%m-%d") if resultado.nacimiento_fecha else "",
            }
        )
    return output_datatable_json(draw, total, data)


@udp_personas_contrapartes.route("/udp_personas_contrapartes")
def list_active():
    """Listado de UDP Personas Contrapartes activos"""
    return render_template(
        "udp_personas_contrapartes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="UDP Personas Contrapartes",
        estatus="A",
    )


@udp_personas_contrapartes.route("/udp_personas_contrapartes/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de UDP Personas Contrapartes inactivos"""
    return render_template(
        "udp_personas_contrapartes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="UDP Personas Contrapartes inactivos",
        estatus="B",
    )


@udp_personas_contrapartes.route("/udp_personas_contrapartes/<int:udp_persona_contraparte_id>")
def detail(udp_persona_contraparte_id):
    """Detalle de un UDP Persona Contraparte"""
    udp_persona_contraparte = UdpPersonaContraparte.query.get_or_404(udp_persona_contraparte_id)
    return render_template("udp_personas_contrapartes/detail.jinja2", udp_persona_contraparte=udp_persona_contraparte)


@udp_personas_contrapartes.route("/udp_personas_contrapartes/nuevo/<int:udp_persona_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(udp_persona_id):
    """Nuevo UDP Persona Contraparte"""
    udp_persona = UdpPersona.query.get_or_404(udp_persona_id)
    form = UdpPersonaContraparteForm()
    if form.validate_on_submit():
        nombres = safe_string(form.nombres.data, save_enie=True)
        apellido_primero = safe_string(form.apellido_primero.data, save_enie=True)
        nacimiento_fecha = form.nacimiento_fecha.data
        # Verificar posible duplicado en la tabla udp_personas
        posible_duplicado = UdpPersona.query.filter(
            UdpPersona.nombres == nombres,
            UdpPersona.apellido_primero == apellido_primero,
            UdpPersona.estatus == "A",
        ).first()
        if posible_duplicado:
            flash(f"Posible duplicado con persona existente: {posible_duplicado.nombre_completo}. Verifique.", "warning")
        udp_persona_contraparte = UdpPersonaContraparte(
            udp_persona_id=udp_persona.id,
            nombres=nombres,
            apellido_primero=apellido_primero,
            apellido_segundo=safe_string(form.apellido_segundo.data, save_enie=True),
            curp=safe_string(form.curp.data),
            nacimiento_fecha=nacimiento_fecha,
            observaciones=safe_string(form.observaciones.data, save_enie=True, max_len=1024),
        )
        udp_persona_contraparte.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(
                f"Nuevo contraparte {udp_persona_contraparte.nombre_completo} para {udp_persona.nombre_completo}"
            ),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("udp_personas_contrapartes/new.jinja2", form=form, udp_persona=udp_persona)


@udp_personas_contrapartes.route("/udp_personas_contrapartes/edicion/<int:udp_persona_contraparte_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_persona_contraparte_id):
    """Editar UDP Persona Contraparte"""
    udp_persona_contraparte = UdpPersonaContraparte.query.get_or_404(udp_persona_contraparte_id)
    form = UdpPersonaContraparteForm()
    if form.validate_on_submit():
        udp_persona_contraparte.nombres = safe_string(form.nombres.data, save_enie=True)
        udp_persona_contraparte.apellido_primero = safe_string(form.apellido_primero.data, save_enie=True)
        udp_persona_contraparte.apellido_segundo = safe_string(form.apellido_segundo.data, save_enie=True)
        udp_persona_contraparte.curp = safe_string(form.curp.data)
        udp_persona_contraparte.nacimiento_fecha = form.nacimiento_fecha.data
        udp_persona_contraparte.observaciones = safe_string(form.observaciones.data, save_enie=True, max_len=1024)
        udp_persona_contraparte.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado contraparte {udp_persona_contraparte.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_contraparte.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombres.data = udp_persona_contraparte.nombres
    form.apellido_primero.data = udp_persona_contraparte.apellido_primero
    form.apellido_segundo.data = udp_persona_contraparte.apellido_segundo
    form.curp.data = udp_persona_contraparte.curp
    form.nacimiento_fecha.data = udp_persona_contraparte.nacimiento_fecha
    form.observaciones.data = udp_persona_contraparte.observaciones
    return render_template("udp_personas_contrapartes/edit.jinja2", form=form, udp_persona_contraparte=udp_persona_contraparte)


@udp_personas_contrapartes.route("/udp_personas_contrapartes/eliminar/<int:udp_persona_contraparte_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_persona_contraparte_id):
    """Eliminar UDP Persona Contraparte"""
    udp_persona_contraparte = UdpPersonaContraparte.query.get_or_404(udp_persona_contraparte_id)
    if udp_persona_contraparte.estatus == "A":
        udp_persona_contraparte.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado contraparte {udp_persona_contraparte.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_contraparte.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_contraparte.udp_persona_id))


@udp_personas_contrapartes.route("/udp_personas_contrapartes/recuperar/<int:udp_persona_contraparte_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_persona_contraparte_id):
    """Recuperar UDP Persona Contraparte"""
    udp_persona_contraparte = UdpPersonaContraparte.query.get_or_404(udp_persona_contraparte_id)
    if udp_persona_contraparte.estatus == "B":
        udp_persona_contraparte.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado contraparte {udp_persona_contraparte.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_contraparte.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_contraparte.udp_persona_id))
