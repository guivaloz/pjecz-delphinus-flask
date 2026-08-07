"""
UDP Visitas, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_personas.models import UdpPersona
from pjecz_delphinus_flask.blueprints.udp_visitas.forms import UdpVisitaForm
from pjecz_delphinus_flask.blueprints.udp_visitas.models import UdpVisita
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_message, safe_string

MODULO = "UDP VISITAS"

udp_visitas = Blueprint("udp_visitas", __name__, template_folder="templates")


@udp_visitas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_visitas.route("/udp_visitas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Visitas"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpVisita.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "udp_persona_id" in request.form:
        consulta = consulta.filter(UdpVisita.udp_persona_id == request.form["udp_persona_id"])
    registros = consulta.order_by(UdpVisita.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "creado": resultado.creado.strftime("%Y-%m-%d %H:%M"),
                    "url": url_for("udp_visitas.detail", udp_visita_id=resultado.id),
                },
                "udp_tipo_visita_nombre": resultado.udp_tipo_visita.nombre,
                "observaciones": (
                    (resultado.observaciones[:48] + "...") if len(resultado.observaciones) > 48 else resultado.observaciones
                ),
            }
        )
    return output_datatable_json(draw, total, data)


@udp_visitas.route("/udp_visitas")
def list_active():
    """Listado de Visitas activas"""
    return render_template(
        "udp_visitas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Visitas",
        estatus="A",
    )


@udp_visitas.route("/udp_visitas/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Visitas inactivas"""
    return render_template(
        "udp_visitas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Visitas eliminadas",
        estatus="B",
    )


@udp_visitas.route("/udp_visitas/<int:udp_visita_id>")
def detail(udp_visita_id):
    """Detalle de una Visita"""
    udp_visita = UdpVisita.query.get_or_404(udp_visita_id)
    return render_template("udp_visitas/detail.jinja2", udp_visita=udp_visita)


@udp_visitas.route("/udp_visitas/nuevo/<int:udp_persona_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(udp_persona_id):
    """Nueva Visita"""
    udp_persona = UdpPersona.query.get_or_404(udp_persona_id)
    form = UdpVisitaForm()
    if form.validate_on_submit():
        udp_visita = UdpVisita(
            udp_persona_id=udp_persona.id,
            udp_tipo_visita_id=form.udp_tipo_visita.data,
            observaciones=safe_string(form.observaciones.data, save_enie=True, max_len=1024),
        )
        udp_visita.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva atención para {udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("udp_visitas/new.jinja2", form=form, udp_persona=udp_persona)


@udp_visitas.route("/udp_visitas/edicion/<int:udp_visita_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_visita_id):
    """Editar Visita"""
    udp_visita = UdpVisita.query.get_or_404(udp_visita_id)
    form = UdpVisitaForm()
    if form.validate_on_submit():
        udp_visita.udp_tipo_visita_id = form.udp_tipo_visita.data
        udp_visita.observaciones = safe_string(form.observaciones.data, save_enie=True, max_len=1024)
        udp_visita.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada atención de {udp_visita.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_visita.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.udp_tipo_visita.data = udp_visita.udp_tipo_visita_id
    form.observaciones.data = udp_visita.observaciones
    return render_template("udp_visitas/edit.jinja2", form=form, udp_visita=udp_visita)


@udp_visitas.route("/udp_visitas/eliminar/<int:udp_visita_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_visita_id):
    """Eliminar Visita"""
    udp_visita = UdpVisita.query.get_or_404(udp_visita_id)
    if udp_visita.estatus == "A":
        udp_visita.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada atención de {udp_visita.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_visita.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_visita.udp_persona_id))


@udp_visitas.route("/udp_visitas/recuperar/<int:udp_visita_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_visita_id):
    """Recuperar Visita"""
    udp_visita = UdpVisita.query.get_or_404(udp_visita_id)
    if udp_visita.estatus == "B":
        udp_visita.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada atención de {udp_visita.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_visita.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_visita.udp_persona_id))
