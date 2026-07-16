"""
UDP Personas Visitas, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_personas.models import UdpPersona
from pjecz_delphinus_flask.blueprints.udp_personas_visitas.forms import UdpPersonaVisitaForm
from pjecz_delphinus_flask.blueprints.udp_personas_visitas.models import UdpPersonaVisita
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_expediente, safe_message, safe_string

MODULO = "UDP PERSONAS VISITAS"

udp_personas_visitas = Blueprint("udp_personas_visitas", __name__, template_folder="templates")


@udp_personas_visitas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_personas_visitas.route("/udp_personas_visitas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de UDP Personas Visitas"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpPersonaVisita.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "udp_persona_id" in request.form:
        consulta = consulta.filter(UdpPersonaVisita.udp_persona_id == request.form["udp_persona_id"])
    registros = consulta.order_by(UdpPersonaVisita.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("udp_personas_visitas.detail", udp_persona_visita_id=resultado.id),
                },
                "udp_tipo_visita_nombre": resultado.udp_tipo_visita.nombre,
                "usuario_email": resultado.usuario.email,
            }
        )
    return output_datatable_json(draw, total, data)


@udp_personas_visitas.route("/udp_personas_visitas")
def list_active():
    """Listado de UDP Personas Visitas activos"""
    return render_template(
        "udp_personas_visitas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Visitas",
        estatus="A",
    )


@udp_personas_visitas.route("/udp_personas_visitas/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de UDP Personas Visitas inactivos"""
    return render_template(
        "udp_personas_visitas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Visitas eliminadas",
        estatus="B",
    )


@udp_personas_visitas.route("/udp_personas_visitas/<int:udp_persona_visita_id>")
def detail(udp_persona_visita_id):
    """Detalle de un UDP Persona Visita"""
    udp_persona_visita = UdpPersonaVisita.query.get_or_404(udp_persona_visita_id)
    return render_template("udp_personas_visitas/detail.jinja2", udp_persona_visita=udp_persona_visita)


@udp_personas_visitas.route("/udp_personas_visitas/nuevo/<int:udp_persona_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(udp_persona_id):
    """Nuevo UDP Persona Visita"""
    udp_persona = UdpPersona.query.get_or_404(udp_persona_id)
    form = UdpPersonaVisitaForm()
    if form.validate_on_submit():
        udp_persona_visita = UdpPersonaVisita(
            udp_persona_id=udp_persona.id,
            udp_tipo_visita_id=form.udp_tipo_visita.data,
            usuario_id=current_user.id,
            observaciones=safe_string(form.observaciones.data, save_enie=True, max_len=1024),
        )
        udp_persona_visita.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva atención para {udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("udp_personas_visitas/new.jinja2", form=form, udp_persona=udp_persona)


@udp_personas_visitas.route("/udp_personas_visitas/edicion/<int:udp_persona_visita_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_persona_visita_id):
    """Editar UDP Persona Visita"""
    udp_persona_visita = UdpPersonaVisita.query.get_or_404(udp_persona_visita_id)
    form = UdpPersonaVisitaForm()
    if form.validate_on_submit():
        udp_persona_visita.udp_tipo_visita_id = form.udp_tipo_visita.data
        udp_persona_visita.observaciones = safe_string(form.observaciones.data, save_enie=True, max_len=1024)
        udp_persona_visita.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada atención de {udp_persona_visita.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_visita.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.udp_tipo_visita.data = udp_persona_visita.udp_tipo_visita_id
    form.observaciones.data = udp_persona_visita.observaciones
    return render_template("udp_personas_visitas/edit.jinja2", form=form, udp_persona_visita=udp_persona_visita)


@udp_personas_visitas.route("/udp_personas_visitas/eliminar/<int:udp_persona_visita_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_persona_visita_id):
    """Eliminar UDP Persona Visita"""
    udp_persona_visita = UdpPersonaVisita.query.get_or_404(udp_persona_visita_id)
    if udp_persona_visita.estatus == "A":
        udp_persona_visita.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada atención de {udp_persona_visita.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_visita.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_visita.udp_persona_id))


@udp_personas_visitas.route("/udp_personas_visitas/recuperar/<int:udp_persona_visita_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_persona_visita_id):
    """Recuperar UDP Persona Visita"""
    udp_persona_visita = UdpPersonaVisita.query.get_or_404(udp_persona_visita_id)
    if udp_persona_visita.estatus == "B":
        udp_persona_visita.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada atención de {udp_persona_visita.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_visita.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_visita.udp_persona_id))
