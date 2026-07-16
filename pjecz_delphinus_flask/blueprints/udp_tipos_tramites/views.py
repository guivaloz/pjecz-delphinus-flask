"""
UDP Tipos Tramites, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_tipos_tramites.forms import UdpTipoTramiteForm
from pjecz_delphinus_flask.blueprints.udp_tipos_tramites.models import UdpTipoTramite
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_message, safe_string

MODULO = "UDP TIPOS TRAMITES"

udp_tipos_tramites = Blueprint("udp_tipos_tramites", __name__, template_folder="templates")


@udp_tipos_tramites.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_tipos_tramites.route("/udp_tipos_tramites/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de UDP Tipos Tramites"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpTipoTramite.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(UdpTipoTramite.nombre.contains(nombre))
    registros = consulta.order_by(UdpTipoTramite.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("udp_tipos_tramites.detail", udp_tipo_tramite_id=resultado.id),
                },
            }
        )
    return output_datatable_json(draw, total, data)


@udp_tipos_tramites.route("/udp_tipos_tramites")
def list_active():
    """Listado de UDP Tipos Tramites activos"""
    return render_template(
        "udp_tipos_tramites/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tipos Trámites",
        estatus="A",
    )


@udp_tipos_tramites.route("/udp_tipos_tramites/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de UDP Tipos Tramites inactivos"""
    return render_template(
        "udp_tipos_tramites/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Tipos Trámites inactivos",
        estatus="B",
    )


@udp_tipos_tramites.route("/udp_tipos_tramites/<int:udp_tipo_tramite_id>")
def detail(udp_tipo_tramite_id):
    """Detalle de un UDP Tipo Tramite"""
    udp_tipo_tramite = UdpTipoTramite.query.get_or_404(udp_tipo_tramite_id)
    return render_template("udp_tipos_tramites/detail.jinja2", udp_tipo_tramite=udp_tipo_tramite)


@udp_tipos_tramites.route("/udp_tipos_tramites/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo UDP Tipo Tramite"""
    form = UdpTipoTramiteForm()
    if form.validate_on_submit():
        nombre = safe_string(form.nombre.data, save_enie=True)
        if UdpTipoTramite.query.filter_by(nombre=nombre).first():
            flash("El nombre ya está en uso. Debe de ser único.", "warning")
            return render_template("udp_tipos_tramites/new.jinja2", form=form)
        udp_tipo_tramite = UdpTipoTramite(nombre=nombre)
        udp_tipo_tramite.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo UDP Tipo Tramite {udp_tipo_tramite.nombre}"),
            url=url_for("udp_tipos_tramites.detail", udp_tipo_tramite_id=udp_tipo_tramite.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("udp_tipos_tramites/new.jinja2", form=form)


@udp_tipos_tramites.route("/udp_tipos_tramites/edicion/<int:udp_tipo_tramite_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_tipo_tramite_id):
    """Editar UDP Tipo Tramite"""
    udp_tipo_tramite = UdpTipoTramite.query.get_or_404(udp_tipo_tramite_id)
    form = UdpTipoTramiteForm()
    if form.validate_on_submit():
        es_valido = True
        nombre = safe_string(form.nombre.data, save_enie=True)
        if udp_tipo_tramite.nombre != nombre:
            udp_tipo_tramite_existente = UdpTipoTramite.query.filter_by(nombre=nombre).first()
            if udp_tipo_tramite_existente and udp_tipo_tramite_existente.id != udp_tipo_tramite.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        if es_valido:
            udp_tipo_tramite.nombre = nombre
            udp_tipo_tramite.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado UDP Tipo Tramite {udp_tipo_tramite.nombre}"),
                url=url_for("udp_tipos_tramites.detail", udp_tipo_tramite_id=udp_tipo_tramite.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombre.data = udp_tipo_tramite.nombre
    return render_template("udp_tipos_tramites/edit.jinja2", form=form, udp_tipo_tramite=udp_tipo_tramite)


@udp_tipos_tramites.route("/udp_tipos_tramites/eliminar/<int:udp_tipo_tramite_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_tipo_tramite_id):
    """Eliminar UDP Tipo Tramite"""
    udp_tipo_tramite = UdpTipoTramite.query.get_or_404(udp_tipo_tramite_id)
    if udp_tipo_tramite.estatus == "A":
        udp_tipo_tramite.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado UDP Tipo Tramite {udp_tipo_tramite.nombre}"),
            url=url_for("udp_tipos_tramites.detail", udp_tipo_tramite_id=udp_tipo_tramite.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_tipos_tramites.detail", udp_tipo_tramite_id=udp_tipo_tramite.id))


@udp_tipos_tramites.route("/udp_tipos_tramites/recuperar/<int:udp_tipo_tramite_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_tipo_tramite_id):
    """Recuperar UDP Tipo Tramite"""
    udp_tipo_tramite = UdpTipoTramite.query.get_or_404(udp_tipo_tramite_id)
    if udp_tipo_tramite.estatus == "B":
        udp_tipo_tramite.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado UDP Tipo Tramite {udp_tipo_tramite.nombre}"),
            url=url_for("udp_tipos_tramites.detail", udp_tipo_tramite_id=udp_tipo_tramite.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_tipos_tramites.detail", udp_tipo_tramite_id=udp_tipo_tramite.id))


@udp_tipos_tramites.route("/udp_tipos_tramites/select_json", methods=["GET", "POST"])
def select_json():
    """Proporcionar el JSON con los ids, nombres para elegir con un select"""
    consulta = UdpTipoTramite.query.filter_by(estatus="A").order_by(UdpTipoTramite.nombre).all()
    resultados = [{"id": s.id, "text": s.nombre} for s in consulta]
    return {"results": resultados, "pagination": {"more": False}}
