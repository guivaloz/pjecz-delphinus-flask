"""
UDP Tipos Condiciones, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.bitacoras.models import Bitacora
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.udp_tipos_condiciones.forms import UdpTipoCondicionForm
from pjecz_delphinus_flask.blueprints.udp_tipos_condiciones.models import UdpTipoCondicion
from pjecz_delphinus_flask.blueprints.usuarios.decorators import permission_required
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_message, safe_string

MODULO = "UDP TIPOS CONDICIONES"

udp_tipos_condiciones = Blueprint("udp_tipos_condiciones", __name__, template_folder="templates")


@udp_tipos_condiciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@udp_tipos_condiciones.route("/udp_tipos_condiciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de UDP Tipos Condiciones"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpTipoCondicion.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(UdpTipoCondicion.nombre.contains(nombre))
    registros = consulta.order_by(UdpTipoCondicion.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("udp_tipos_condiciones.detail", udp_tipo_condicion_id=resultado.id),
                },
            }
        )
    return output_datatable_json(draw, total, data)


@udp_tipos_condiciones.route("/udp_tipos_condiciones")
def list_active():
    """Listado de UDP Tipos Condiciones activos"""
    return render_template(
        "udp_tipos_condiciones/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tipos Condiciones",
        estatus="A",
    )


@udp_tipos_condiciones.route("/udp_tipos_condiciones/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de UDP Tipos Condiciones inactivos"""
    return render_template(
        "udp_tipos_condiciones/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Tipos Condiciones inactivos",
        estatus="B",
    )


@udp_tipos_condiciones.route("/udp_tipos_condiciones/<int:udp_tipo_condicion_id>")
def detail(udp_tipo_condicion_id):
    """Detalle de un UDP Tipo Condicion"""
    udp_tipo_condicion = UdpTipoCondicion.query.get_or_404(udp_tipo_condicion_id)
    return render_template("udp_tipos_condiciones/detail.jinja2", udp_tipo_condicion=udp_tipo_condicion)


@udp_tipos_condiciones.route("/udp_tipos_condiciones/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo UDP Tipo Condicion"""
    form = UdpTipoCondicionForm()
    if form.validate_on_submit():
        nombre = safe_string(form.nombre.data, save_enie=True)
        if UdpTipoCondicion.query.filter_by(nombre=nombre).first():
            flash("El nombre ya está en uso. Debe de ser único.", "warning")
            return render_template("udp_tipos_condiciones/new.jinja2", form=form)
        udp_tipo_condicion = UdpTipoCondicion(nombre=nombre)
        udp_tipo_condicion.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo UDP Tipo Condicion {udp_tipo_condicion.nombre}"),
            url=url_for("udp_tipos_condiciones.detail", udp_tipo_condicion_id=udp_tipo_condicion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("udp_tipos_condiciones/new.jinja2", form=form)


@udp_tipos_condiciones.route("/udp_tipos_condiciones/edicion/<int:udp_tipo_condicion_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(udp_tipo_condicion_id):
    """Editar UDP Tipo Condicion"""
    udp_tipo_condicion = UdpTipoCondicion.query.get_or_404(udp_tipo_condicion_id)
    form = UdpTipoCondicionForm()
    if form.validate_on_submit():
        es_valido = True
        nombre = safe_string(form.nombre.data, save_enie=True)
        if udp_tipo_condicion.nombre != nombre:
            udp_tipo_condicion_existente = UdpTipoCondicion.query.filter_by(nombre=nombre).first()
            if udp_tipo_condicion_existente and udp_tipo_condicion_existente.id != udp_tipo_condicion.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        if es_valido:
            udp_tipo_condicion.nombre = nombre
            udp_tipo_condicion.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado UDP Tipo Condicion {udp_tipo_condicion.nombre}"),
                url=url_for("udp_tipos_condiciones.detail", udp_tipo_condicion_id=udp_tipo_condicion.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombre.data = udp_tipo_condicion.nombre
    return render_template("udp_tipos_condiciones/edit.jinja2", form=form, udp_tipo_condicion=udp_tipo_condicion)


@udp_tipos_condiciones.route("/udp_tipos_condiciones/eliminar/<int:udp_tipo_condicion_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(udp_tipo_condicion_id):
    """Eliminar UDP Tipo Condicion"""
    udp_tipo_condicion = UdpTipoCondicion.query.get_or_404(udp_tipo_condicion_id)
    if udp_tipo_condicion.estatus == "A":
        udp_tipo_condicion.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado UDP Tipo Condicion {udp_tipo_condicion.nombre}"),
            url=url_for("udp_tipos_condiciones.detail", udp_tipo_condicion_id=udp_tipo_condicion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_tipos_condiciones.detail", udp_tipo_condicion_id=udp_tipo_condicion.id))


@udp_tipos_condiciones.route("/udp_tipos_condiciones/recuperar/<int:udp_tipo_condicion_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(udp_tipo_condicion_id):
    """Recuperar UDP Tipo Condicion"""
    udp_tipo_condicion = UdpTipoCondicion.query.get_or_404(udp_tipo_condicion_id)
    if udp_tipo_condicion.estatus == "B":
        udp_tipo_condicion.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado UDP Tipo Condicion {udp_tipo_condicion.nombre}"),
            url=url_for("udp_tipos_condiciones.detail", udp_tipo_condicion_id=udp_tipo_condicion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("udp_tipos_condiciones.detail", udp_tipo_condicion_id=udp_tipo_condicion.id))


@udp_tipos_condiciones.route("/udp_tipos_condiciones/select_json", methods=["GET", "POST"])
def select_json():
    """Proporcionar el JSON con los ids, nombres para elegir con un select"""
    consulta = UdpTipoCondicion.query.filter_by(estatus="A").order_by(UdpTipoCondicion.nombre).all()
    resultados = [{"id": s.id, "text": s.nombre} for s in consulta]
    return {"results": resultados, "pagination": {"more": False}}
