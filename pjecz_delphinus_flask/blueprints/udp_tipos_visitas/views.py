"""
UDP Tipos Visitas, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_tipos_visitas.forms import UdpTipoVisitaForm
from pjecz_delphinus_flask.blueprints.udp_tipos_visitas.models import UdpTipoVisita
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_message, safe_string

MODULO = "UDP TIPOS VISITAS"

udp_tipos_visitas = Blueprint("udp_tipos_visitas", __name__, template_folder="templates")


@udp_tipos_visitas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_tipos_visitas.route("/udp_tipos_visitas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de UDP Tipos Visitas"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpTipoVisita.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(UdpTipoVisita.nombre.contains(nombre))
    registros = consulta.order_by(UdpTipoVisita.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("udp_tipos_visitas.detail", udp_tipo_visita_id=resultado.id),
                },
            }
        )
    return output_datatable_json(draw, total, data)


@udp_tipos_visitas.route("/udp_tipos_visitas")
def list_active():
    """Listado de UDP Tipos Visitas activos"""
    return render_template(
        "udp_tipos_visitas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tipos Visitas",
        estatus="A",
    )


@udp_tipos_visitas.route("/udp_tipos_visitas/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de UDP Tipos Visitas inactivos"""
    return render_template(
        "udp_tipos_visitas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Tipos Visitas inactivos",
        estatus="B",
    )


@udp_tipos_visitas.route("/udp_tipos_visitas/<int:udp_tipo_visita_id>")
def detail(udp_tipo_visita_id):
    """Detalle de un UDP Tipo Visita"""
    udp_tipo_visita = UdpTipoVisita.query.get_or_404(udp_tipo_visita_id)
    return render_template("udp_tipos_visitas/detail.jinja2", udp_tipo_visita=udp_tipo_visita)


@udp_tipos_visitas.route("/udp_tipos_visitas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo UDP Tipo Visita"""
    form = UdpTipoVisitaForm()
    if form.validate_on_submit():
        nombre = safe_string(form.nombre.data, save_enie=True)
        if UdpTipoVisita.query.filter_by(nombre=nombre).first():
            flash("El nombre ya está en uso. Debe de ser único.", "warning")
            return render_template("udp_tipos_visitas/new.jinja2", form=form)
        udp_tipo_visita = UdpTipoVisita(nombre=nombre)
        udp_tipo_visita.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo UDP Tipo Visita {udp_tipo_visita.nombre}"),
            url=url_for("udp_tipos_visitas.detail", udp_tipo_visita_id=udp_tipo_visita.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("udp_tipos_visitas/new.jinja2", form=form)


@udp_tipos_visitas.route("/udp_tipos_visitas/edicion/<int:udp_tipo_visita_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_tipo_visita_id):
    """Editar UDP Tipo Visita"""
    udp_tipo_visita = UdpTipoVisita.query.get_or_404(udp_tipo_visita_id)
    form = UdpTipoVisitaForm()
    if form.validate_on_submit():
        es_valido = True
        nombre = safe_string(form.nombre.data, save_enie=True)
        if udp_tipo_visita.nombre != nombre:
            udp_tipo_visita_existente = UdpTipoVisita.query.filter_by(nombre=nombre).first()
            if udp_tipo_visita_existente and udp_tipo_visita_existente.id != udp_tipo_visita.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        if es_valido:
            udp_tipo_visita.nombre = nombre
            udp_tipo_visita.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado UDP Tipo Visita {udp_tipo_visita.nombre}"),
                url=url_for("udp_tipos_visitas.detail", udp_tipo_visita_id=udp_tipo_visita.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombre.data = udp_tipo_visita.nombre
    return render_template("udp_tipos_visitas/edit.jinja2", form=form, udp_tipo_visita=udp_tipo_visita)


@udp_tipos_visitas.route("/udp_tipos_visitas/eliminar/<int:udp_tipo_visita_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_tipo_visita_id):
    """Eliminar UDP Tipo Visita"""
    udp_tipo_visita = UdpTipoVisita.query.get_or_404(udp_tipo_visita_id)
    if udp_tipo_visita.estatus == "A":
        udp_tipo_visita.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado UDP Tipo Visita {udp_tipo_visita.nombre}"),
            url=url_for("udp_tipos_visitas.detail", udp_tipo_visita_id=udp_tipo_visita.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_tipos_visitas.detail", udp_tipo_visita_id=udp_tipo_visita.id))


@udp_tipos_visitas.route("/udp_tipos_visitas/recuperar/<int:udp_tipo_visita_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_tipo_visita_id):
    """Recuperar UDP Tipo Visita"""
    udp_tipo_visita = UdpTipoVisita.query.get_or_404(udp_tipo_visita_id)
    if udp_tipo_visita.estatus == "B":
        udp_tipo_visita.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado UDP Tipo Visita {udp_tipo_visita.nombre}"),
            url=url_for("udp_tipos_visitas.detail", udp_tipo_visita_id=udp_tipo_visita.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_tipos_visitas.detail", udp_tipo_visita_id=udp_tipo_visita.id))
