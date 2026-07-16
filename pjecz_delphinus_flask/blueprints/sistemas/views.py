"""
Sistemas
"""

from flask import Blueprint, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required

from pjecz_delphinus_flask.blueprints.udp_personas.models import UdpPersona
from pjecz_delphinus_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_delphinus_flask.lib.safe_string import safe_string

sistemas = Blueprint("sistemas", __name__, template_folder="templates")


@sistemas.route("/")
def start():
    """Pagina Inicial"""

    # Si el usuario está autenticado
    if current_user.is_authenticated:
        # Mostrar start.jinja2
        return render_template("sistemas/start.jinja2")

    # No está autenticado, debe de iniciar sesión
    return redirect("/login")


@sistemas.route("/sistemas/ultimas_personas_datatable_json", methods=["GET", "POST"])
@login_required
def ultimas_personas_datatable_json():
    """DataTable JSON para las últimas 10 personas agregadas"""
    draw, start, rows_per_page = get_datatable_parameters()
    consulta = UdpPersona.query
    consulta = consulta.filter_by(estatus="A")
    if "nombres" in request.form:
        nombres = safe_string(request.form["nombres"], save_enie=True)
        if nombres != "":
            consulta = consulta.filter(UdpPersona.nombres.contains(nombres))
    if "apellido_primero" in request.form:
        apellido_primero = safe_string(request.form["apellido_primero"], save_enie=True)
        if apellido_primero != "":
            consulta = consulta.filter(UdpPersona.apellido_primero.contains(apellido_primero))
    if "apellido_segundo" in request.form:
        apellido_segundo = safe_string(request.form["apellido_segundo"], save_enie=True)
        if apellido_segundo != "":
            consulta = consulta.filter(UdpPersona.apellido_segundo.contains(apellido_segundo))
    if "curp" in request.form:
        curp = safe_string(request.form["curp"])
        if curp != "":
            consulta = consulta.filter(UdpPersona.curp.contains(curp))
    registros = consulta.order_by(UdpPersona.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre_completo": resultado.nombre_completo,
                    "url": url_for("udp_personas.detail", udp_persona_id=resultado.id),
                },
                "curp": resultado.curp or "",
                "nacimiento_fecha": resultado.nacimiento_fecha.strftime("%Y-%m-%d") if resultado.nacimiento_fecha else "",
                "udp_sexo_nombre": resultado.udp_sexo.nombre,
            }
        )
    return output_datatable_json(draw, total, data)


@sistemas.route("/favicon.ico")
def favicon():
    """Favicon"""
    return send_from_directory("static/img", "favicon.ico", mimetype="image/vnd.microsoft.icon")


@sistemas.app_errorhandler(400)
def bad_request(error):
    """Solicitud errónea"""
    return render_template("sistemas/403.jinja2", error=error), 403


@sistemas.app_errorhandler(403)
def forbidden(error):
    """Acceso no autorizado"""
    return render_template("sistemas/403.jinja2"), 403


@sistemas.app_errorhandler(404)
def page_not_found(error):
    """Error página no encontrada"""
    return render_template("sistemas/404.jinja2"), 404


@sistemas.app_errorhandler(500)
def internal_server_error(error):
    """Error del servidor"""
    return render_template("sistemas/500.jinja2"), 500
