"""
UDP Sexos, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_sexos.forms import UdpSexoForm
from pjecz_delphinus_flask.blueprints.udp_sexos.models import UdpSexo
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_message, safe_string

MODULO = "UDP SEXOS"

udp_sexos = Blueprint("udp_sexos", __name__, template_folder="templates")


@udp_sexos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_sexos.route("/udp_sexos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de UDP Sexos"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpSexo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(UdpSexo.nombre.contains(nombre))
    registros = consulta.order_by(UdpSexo.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("udp_sexos.detail", udp_sexo_id=resultado.id),
                },
            }
        )
    return output_datatable_json(draw, total, data)


@udp_sexos.route("/udp_sexos")
def list_active():
    """Listado de UDP Sexos activos"""
    return render_template(
        "udp_sexos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Sexos",
        estatus="A",
    )


@udp_sexos.route("/udp_sexos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de UDP Sexos inactivos"""
    return render_template(
        "udp_sexos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Sexos inactivos",
        estatus="B",
    )


@udp_sexos.route("/udp_sexos/<int:udp_sexo_id>")
def detail(udp_sexo_id):
    """Detalle de un UDP Sexo"""
    udp_sexo = UdpSexo.query.get_or_404(udp_sexo_id)
    return render_template("udp_sexos/detail.jinja2", udp_sexo=udp_sexo)


@udp_sexos.route("/udp_sexos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo UDP Sexo"""
    form = UdpSexoForm()
    if form.validate_on_submit():
        nombre = safe_string(form.nombre.data, save_enie=True)
        if UdpSexo.query.filter_by(nombre=nombre).first():
            flash("El nombre ya está en uso. Debe de ser único.", "warning")
            return render_template("udp_sexos/new.jinja2", form=form)
        udp_sexo = UdpSexo(nombre=nombre)
        udp_sexo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo UDP Sexo {udp_sexo.nombre}"),
            url=url_for("udp_sexos.detail", udp_sexo_id=udp_sexo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("udp_sexos/new.jinja2", form=form)


@udp_sexos.route("/udp_sexos/edicion/<int:udp_sexo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_sexo_id):
    """Editar UDP Sexo"""
    udp_sexo = UdpSexo.query.get_or_404(udp_sexo_id)
    form = UdpSexoForm()
    if form.validate_on_submit():
        es_valido = True
        nombre = safe_string(form.nombre.data, save_enie=True)
        if udp_sexo.nombre != nombre:
            udp_sexo_existente = UdpSexo.query.filter_by(nombre=nombre).first()
            if udp_sexo_existente and udp_sexo_existente.id != udp_sexo.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        if es_valido:
            udp_sexo.nombre = nombre
            udp_sexo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado UDP Sexo {udp_sexo.nombre}"),
                url=url_for("udp_sexos.detail", udp_sexo_id=udp_sexo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombre.data = udp_sexo.nombre
    return render_template("udp_sexos/edit.jinja2", form=form, udp_sexo=udp_sexo)


@udp_sexos.route("/udp_sexos/eliminar/<int:udp_sexo_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_sexo_id):
    """Eliminar UDP Sexo"""
    udp_sexo = UdpSexo.query.get_or_404(udp_sexo_id)
    if udp_sexo.estatus == "A":
        udp_sexo.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado UDP Sexo {udp_sexo.nombre}"),
            url=url_for("udp_sexos.detail", udp_sexo_id=udp_sexo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_sexos.detail", udp_sexo_id=udp_sexo.id))


@udp_sexos.route("/udp_sexos/recuperar/<int:udp_sexo_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_sexo_id):
    """Recuperar UDP Sexo"""
    udp_sexo = UdpSexo.query.get_or_404(udp_sexo_id)
    if udp_sexo.estatus == "B":
        udp_sexo.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado UDP Sexo {udp_sexo.nombre}"),
            url=url_for("udp_sexos.detail", udp_sexo_id=udp_sexo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_sexos.detail", udp_sexo_id=udp_sexo.id))


@udp_sexos.route("/udp_sexos/select_json", methods=["GET", "POST"])
def select_json():
    """Proporcionar el JSON con los ids, nombres para elegir con un select"""
    consulta = UdpSexo.query.filter_by(estatus="A").order_by(UdpSexo.nombre).all()
    resultados = [{"id": s.id, "text": s.nombre} for s in consulta]
    return {"results": resultados, "pagination": {"more": False}}
