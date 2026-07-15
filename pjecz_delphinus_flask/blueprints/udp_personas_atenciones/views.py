"""
UDP Personas Atenciones, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.autoridades.models import Autoridad
from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.distritos.models import Distrito
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_personas.models import UdpPersona
from pjecz_delphinus_flask.blueprints.udp_personas_atenciones.forms import UdpPersonaAtencionForm
from pjecz_delphinus_flask.blueprints.udp_personas_atenciones.models import UdpPersonaAtencion
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_expediente, safe_message, safe_string

MODULO = "UDP PERSONAS ATENCIONES"

udp_personas_atenciones = Blueprint("udp_personas_atenciones", __name__, template_folder="templates")


@udp_personas_atenciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_personas_atenciones.route("/udp_personas_atenciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de UDP Personas Atenciones"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpPersonaAtencion.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "udp_persona_id" in request.form:
        consulta = consulta.filter(UdpPersonaAtencion.udp_persona_id == request.form["udp_persona_id"])
    registros = consulta.order_by(UdpPersonaAtencion.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("udp_personas_atenciones.detail", udp_persona_atencion_id=resultado.id),
                },
                "udp_tipo_tramite_nombre": resultado.udp_tipo_tramite.nombre,
                "usuario_email": resultado.usuario.email,
                "autoridad_clave": resultado.autoridad.clave,
                "expediente": resultado.expediente or "",
            }
        )
    return output_datatable_json(draw, total, data)


@udp_personas_atenciones.route("/udp_personas_atenciones")
def list_active():
    """Listado de UDP Personas Atenciones activos"""
    return render_template(
        "udp_personas_atenciones/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Atenciones",
        estatus="A",
    )


@udp_personas_atenciones.route("/udp_personas_atenciones/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de UDP Personas Atenciones inactivos"""
    return render_template(
        "udp_personas_atenciones/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Atenciones eliminadas",
        estatus="B",
    )


@udp_personas_atenciones.route("/udp_personas_atenciones/<int:udp_persona_atencion_id>")
def detail(udp_persona_atencion_id):
    """Detalle de un UDP Persona Atencion"""
    udp_persona_atencion = UdpPersonaAtencion.query.get_or_404(udp_persona_atencion_id)
    return render_template("udp_personas_atenciones/detail.jinja2", udp_persona_atencion=udp_persona_atencion)


@udp_personas_atenciones.route("/udp_personas_atenciones/nuevo/<int:udp_persona_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(udp_persona_id):
    """Nuevo UDP Persona Atencion"""
    udp_persona = UdpPersona.query.get_or_404(udp_persona_id)
    form = UdpPersonaAtencionForm()
    if form.validate_on_submit():
        expediente = ""
        if form.expediente.data:
            try:
                expediente = safe_expediente(form.expediente.data)
            except ValueError:
                flash("El expediente no es válido.", "warning")
                return render_template("udp_personas_atenciones/new.jinja2", form=form, udp_persona=udp_persona)
        udp_persona_atencion = UdpPersonaAtencion(
            udp_persona_id=udp_persona.id,
            udp_tipo_tramite_id=form.udp_tipo_tramite.data,
            usuario_id=current_user.id,
            autoridad_id=form.autoridad.data,
            expediente=expediente,
            observaciones=safe_string(form.observaciones.data, save_enie=True, max_len=1024),
        )
        udp_persona_atencion.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva atención para {udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template(
        "udp_personas_atenciones/new.jinja2",
        form=form,
        udp_persona=udp_persona,
        distrito_por_defecto=Distrito.query.filter_by(clave="ND").first(),
        autoridad_por_defecto=Autoridad.query.filter_by(clave="ND").first(),
    )


@udp_personas_atenciones.route("/udp_personas_atenciones/edicion/<int:udp_persona_atencion_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_persona_atencion_id):
    """Editar UDP Persona Atencion"""
    udp_persona_atencion = UdpPersonaAtencion.query.get_or_404(udp_persona_atencion_id)
    form = UdpPersonaAtencionForm()
    if form.validate_on_submit():
        expediente = ""
        if form.expediente.data:
            try:
                expediente = safe_expediente(form.expediente.data)
            except ValueError:
                flash("El expediente no es válido.", "warning")
                return render_template(
                    "udp_personas_atenciones/edit.jinja2", form=form, udp_persona_atencion=udp_persona_atencion
                )
        udp_persona_atencion.udp_tipo_tramite_id = form.udp_tipo_tramite.data
        udp_persona_atencion.autoridad_id = form.autoridad.data
        udp_persona_atencion.expediente = expediente
        udp_persona_atencion.observaciones = safe_string(form.observaciones.data, save_enie=True, max_len=1024)
        udp_persona_atencion.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada atención de {udp_persona_atencion.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_atencion.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.udp_tipo_tramite.data = udp_persona_atencion.udp_tipo_tramite_id
    form.autoridad.data = udp_persona_atencion.autoridad_id
    form.expediente.data = udp_persona_atencion.expediente
    form.observaciones.data = udp_persona_atencion.observaciones
    return render_template("udp_personas_atenciones/edit.jinja2", form=form, udp_persona_atencion=udp_persona_atencion)


@udp_personas_atenciones.route("/udp_personas_atenciones/eliminar/<int:udp_persona_atencion_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_persona_atencion_id):
    """Eliminar UDP Persona Atencion"""
    udp_persona_atencion = UdpPersonaAtencion.query.get_or_404(udp_persona_atencion_id)
    if udp_persona_atencion.estatus == "A":
        udp_persona_atencion.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada atención de {udp_persona_atencion.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_atencion.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_atencion.udp_persona_id))


@udp_personas_atenciones.route("/udp_personas_atenciones/recuperar/<int:udp_persona_atencion_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_persona_atencion_id):
    """Recuperar UDP Persona Atencion"""
    udp_persona_atencion = UdpPersonaAtencion.query.get_or_404(udp_persona_atencion_id)
    if udp_persona_atencion.estatus == "B":
        udp_persona_atencion.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada atención de {udp_persona_atencion.udp_persona.nombre_completo}"),
            url=url_for("udp_personas.detail", udp_persona_id=udp_persona_atencion.udp_persona_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_personas.detail", udp_persona_id=udp_persona_atencion.udp_persona_id))
