"""
CLI DB
"""

import csv
import os
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress
from typer import Typer

from pjecz_delphinus_flask.app import app
from pjecz_delphinus_flask.blueprints.autoridades.models import Autoridad
from pjecz_delphinus_flask.blueprints.distritos.models import Distrito
from pjecz_delphinus_flask.blueprints.modulos.models import Modulo
from pjecz_delphinus_flask.blueprints.permisos.models import Permiso
from pjecz_delphinus_flask.blueprints.roles.models import Rol
from pjecz_delphinus_flask.blueprints.usuarios.models import Usuario
from pjecz_delphinus_flask.blueprints.usuarios_roles.models import UsuarioRol
from pjecz_delphinus_flask.config.extensions import database, pwd_context
from pjecz_delphinus_flask.lib.pwgen import generar_contrasena
from pjecz_delphinus_flask.lib.safe_string import safe_clave, safe_email, safe_string

# Rutas a los archivos CSV
AUTORIDADES_CSV = "seed/autoridades.csv"
DISTRITOS_CSV = "seed/distritos.csv"
MODULOS_CSV = "seed/modulos.csv"
PERMISOS_CSV = "seed/roles_permisos.csv"
ROLES_CSV = "seed/roles_permisos.csv"
USUARIOS_CSV = "seed/usuarios_roles.csv"
USUARIOS_ROLES_CSV = "seed/usuarios_roles.csv"

# Cargar variables de entorno
load_dotenv()
DEPLOYMENT_ENVIRONMENT = os.getenv("DEPLOYMENT_ENVIRONMENT", "DEVELOPMENT").upper()
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME")

# Inicializar la aplicación
app.app_context().push()

db = Typer()


def alimentar_modulos():
    """Alimentar Modulos"""
    console = Console()
    ruta_csv = Path(MODULOS_CSV)
    if not ruta_csv.exists():
        console.print(f"[red]ERROR: {ruta_csv.name} no se encontró.")
        sys.exit(1)
    if not ruta_csv.is_file():
        console.print(f"[red]ERROR: {ruta_csv.name} no es un archivo.")
        sys.exit(1)
    console.print("Alimentando modulos...")
    contador = 0
    with open(ruta_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            modulo_id = int(row["modulo_id"])
            nombre = safe_string(row["nombre"], save_enie=True)
            nombre_corto = safe_string(row["nombre_corto"], do_unidecode=False, save_enie=True, to_uppercase=False)
            icono = row["icono"]
            ruta = row["ruta"]
            en_navegacion = row["en_navegacion"] == "1"
            estatus = row["estatus"]
            if modulo_id != contador + 1:
                console.print(f"[red]ERROR: modulo_id {modulo_id} no es consecutivo")
                sys.exit(1)
            Modulo(
                nombre=nombre,
                nombre_corto=nombre_corto,
                icono=icono,
                ruta=ruta,
                en_navegacion=en_navegacion,
                estatus=estatus,
            ).save()
            contador += 1
    console.print(f"[green]{contador} modulos alimentados.")


def alimentar_roles():
    """Alimentar Roles"""
    console = Console()
    ruta = Path(ROLES_CSV)
    if not ruta.exists():
        console.print(f"[red]ERROR: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        console.print(f"[red]ERROR: {ruta.name} no es un archivo.")
        sys.exit(1)
    console.print("Alimentando roles...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            rol_id = int(row["rol_id"])
            nombre = safe_string(row["nombre"], save_enie=True)
            estatus = row["estatus"]
            if rol_id != contador + 1:
                console.print(f"[red]ERROR: rol_id {rol_id} no es consecutivo")
                sys.exit(1)
            Rol(
                nombre=nombre,
                estatus=estatus,
            ).save()
            contador += 1
    console.print(f"[green]{contador} roles alimentados.")


def alimentar_permisos():
    """Alimentar Permisos"""
    console = Console()
    ruta = Path(PERMISOS_CSV)
    if not ruta.exists():
        console.print(f"[red]ERROR: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        console.print(f"[red]ERROR: {ruta.name} no es un archivo.")
        sys.exit(1)
    modulos = Modulo.query.all()
    if len(modulos) == 0:
        console.print("[red]ERROR: No hay modulos alimentados.")
        sys.exit(1)
    console.print("Alimentando permisos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            rol_id = int(row["rol_id"])
            estatus = row["estatus"]
            rol = Rol.query.get(rol_id)
            if rol is None:
                console.print(f"[red]ERROR: rol_id {rol_id} no existe")
                sys.exit(1)
            for modulo in modulos:
                columna = modulo.nombre.lower()
                if columna not in row:
                    continue
                if row[columna] == "":
                    continue
                try:
                    nivel = int(row[columna])
                except ValueError:
                    nivel = 0
                if nivel < 0:
                    nivel = 0
                if nivel > 4:
                    nivel = 4
                Permiso(
                    rol=rol,
                    modulo=modulo,
                    nivel=nivel,
                    nombre=f"{rol.nombre} puede {Permiso.NIVELES[nivel]} en {modulo.nombre}",
                    estatus=estatus,
                ).save()
            contador += 1
    console.print(f"[green]{contador} permisos alimentados.")


def alimentar_distritos():
    """Alimentar Distritos"""
    console = Console()
    ruta = Path(DISTRITOS_CSV)
    if not ruta.exists():
        console.print(f"[red]ERROR: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        console.print(f"[red]ERROR: {ruta.name} no es un archivo.")
        sys.exit(1)
    console.print("Alimentando distritos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            distrito_id = int(row["distrito_id"])
            clave = safe_clave(row["clave"])
            nombre = safe_string(row["nombre"], save_enie=True)
            nombre_corto = safe_string(row["nombre_corto"], save_enie=True)
            estatus = row["estatus"]
            if distrito_id != contador + 1:
                console.print(f"[red]ERROR: distrito_id {distrito_id} no es consecutivo")
                sys.exit(1)
            Distrito(
                clave=clave,
                nombre=nombre,
                nombre_corto=nombre_corto,
                estatus=estatus,
            ).save()
            contador += 1
    console.print(f"[green]{contador} distritos alimentados.")


def alimentar_autoridades():
    """Alimentar Autoridades"""
    console = Console()
    ruta = Path(AUTORIDADES_CSV)
    if not ruta.exists():
        console.print(f"[red]ERROR: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        console.print(f"[red]ERROR: {ruta.name} no es un archivo.")
        sys.exit(1)
    distrito_nd = Distrito.query.filter_by(clave="ND").first()
    if distrito_nd is None:
        console.print("[red]ERROR: No se encontró el distrito 'ND'.")
        sys.exit(1)
    console.print("Alimentando autoridades...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Si autoridad_id NO es consecutivo, se inserta una autoridad "NO EXISTE"
            autoridad_id = int(row["autoridad_id"])
            while autoridad_id > contador + 1:
                Autoridad(
                    distrito_id=distrito_nd.id,
                    clave=f"NE-{contador}",
                    descripcion="NO EXISTE",
                    descripcion_corta="NO EXISTE",
                    estatus="B",
                ).save()
                contador += 1
            distrito_id = int(row["distrito_id"])
            distrito = Distrito.query.get(distrito_id)
            if distrito is None:
                console.print(f"[red]AVISO: distrito_id {distrito_id} no existe")
                sys.exit(1)
            clave = safe_clave(row["clave"])
            descripcion = safe_string(row["descripcion"], save_enie=True)
            descripcion_corta = safe_string(row["descripcion_corta"], save_enie=True)
            estatus = row["estatus"]
            Autoridad(
                distrito=distrito,
                clave=clave,
                descripcion=descripcion,
                descripcion_corta=descripcion_corta,
                estatus=estatus,
            ).save()
            contador += 1
    console.print(f"[green]{contador} autoridades alimentadas.")


def alimentar_usuarios():
    """Alimentar Usuarios"""
    console = Console()
    ruta = Path(USUARIOS_CSV)
    if not ruta.exists():
        console.print(f"[red]ERROR: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        console.print(f"[red]ERROR: {ruta.name} no es un archivo.")
        sys.exit(1)
    autoridad_nd = Autoridad.query.filter_by(clave="ND").first()
    if autoridad_nd is None:
        console.print("[red]ERROR: No se encontró la autoridad 'ND'.")
        sys.exit(1)
    console.print("Alimentando usuarios...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Si usuario_id NO es consecutivo, se inserta un usuario "NO EXISTE"
            usuario_id = int(row["usuario_id"])
            while usuario_id > contador + 1:
                Usuario(
                    autoridad_id=autoridad_nd.id,
                    email=f"no-existe-{contador}@server.com",
                    nombres="NO EXISTE",
                    apellido_paterno="",
                    apellido_materno="",
                    curp="",
                    puesto="",
                    estatus="B",
                    api_key="",
                    api_key_expiracion=datetime(year=2000, month=1, day=1),
                    contrasena=pwd_context.hash(generar_contrasena()),
                ).save()
                contador += 1
            autoridad_clave = safe_clave(row["autoridad_clave"])
            email = safe_email(row["email"])
            nombres = safe_string(row["nombres"], save_enie=True)
            apellido_paterno = safe_string(row["apellido_paterno"], save_enie=True)
            apellido_materno = safe_string(row["apellido_materno"], save_enie=True)
            curp = safe_string(row["curp"])
            puesto = safe_string(row["puesto"], save_enie=True)
            estatus = row["estatus"]
            autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
            if autoridad is None:
                console.print(f"[red]ERROR: autoridad_clave {autoridad_clave} no existe")
                sys.exit(1)
            Usuario(
                autoridad=autoridad,
                email=email,
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                curp=curp,
                puesto=puesto,
                estatus=estatus,
                api_key="",
                api_key_expiracion=datetime(year=2000, month=1, day=1),
                contrasena=pwd_context.hash(generar_contrasena()),
            ).save()
            contador += 1
    console.print(f"[green]{contador} usuarios alimentados.")


def alimentar_usuarios_roles():
    """Alimentar Usuarios-Roles"""
    console = Console()
    ruta = Path(USUARIOS_ROLES_CSV)
    if not ruta.exists():
        console.print(f"[red]ERROR: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        console.print(f"[red]ERROR: {ruta.name} no es un archivo.")
        sys.exit(1)
    usuarios_que_no_existen = []
    console.print("Alimentando usuarios-roles...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            usuario_id = int(row["usuario_id"])
            usuario = Usuario.query.get(usuario_id)
            if usuario is None:
                usuarios_que_no_existen.append(str(usuario_id))
                continue
            for rol_nombre in row["roles"].split(","):
                rol_nombre = rol_nombre.strip().upper()
                rol = Rol.query.filter_by(nombre=rol_nombre).first()
                if rol is None:
                    continue
                UsuarioRol(
                    usuario=usuario,
                    rol=rol,
                    descripcion=f"{usuario.email} en {rol.nombre}",
                ).save()
                contador += 1
    if usuarios_que_no_existen:
        console.print(f"[yellow]AVISO: {','.join(usuarios_que_no_existen)} usuarios no existen.")
    console.print(f"[green]{contador} usuarios-roles alimentados.")


def respaldar_autoridades():
    """Respaldar Autoridades"""
    console = Console()
    ruta = Path(AUTORIDADES_CSV)
    if ruta.exists():
        console.print(f"[red]ERROR: {AUTORIDADES_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    console.print("Respaldando autoridades...")
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "autoridad_id",
                "distrito_id",
                "clave",
                "descripcion",
                "descripcion_corta",
                "estatus",
            ]
        )
        for autoridad in Autoridad.query.order_by(Autoridad.id).all():
            respaldo.writerow(
                [
                    autoridad.id,
                    autoridad.distrito_id,
                    autoridad.clave,
                    autoridad.descripcion,
                    autoridad.descripcion_corta,
                    autoridad.estatus,
                ]
            )
            contador += 1
    console.print(f"[green]{contador} autoridades respaldadas.")


def respaldar_distritos():
    """Respaldar Distritos"""
    console = Console()
    ruta = Path(DISTRITOS_CSV)
    if ruta.exists():
        console.print(f"[red]ERROR: {DISTRITOS_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    console.print("Respaldando distritos...")
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "distrito_id",
                "clave",
                "nombre",
                "nombre_corto",
                "estatus",
            ]
        )
        for distrito in Distrito.query.order_by(Distrito.id).all():
            respaldo.writerow(
                [
                    distrito.id,
                    distrito.clave,
                    distrito.nombre,
                    distrito.nombre_corto,
                    distrito.estatus,
                ]
            )
            contador += 1
    console.print(f"[green]{contador} distritos respaldados.")


def respaldar_modulos():
    """Respaldar Modulos"""
    console = Console()
    ruta = Path(MODULOS_CSV)
    if ruta.exists():
        console.print(f"[red]ERROR: {MODULOS_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    console.print("Respaldando modulos...")
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "modulo_id",
                "nombre",
                "nombre_corto",
                "icono",
                "ruta",
                "en_navegacion",
                "estatus",
            ]
        )
        for modulo in Modulo.query.order_by(Modulo.id).all():
            respaldo.writerow(
                [
                    modulo.id,
                    modulo.nombre,
                    modulo.nombre_corto,
                    modulo.icono,
                    modulo.ruta,
                    int(modulo.en_navegacion),
                    modulo.estatus,
                ]
            )
            contador += 1
    console.print(f"[green]{contador} modulos respaldados.")


def respaldar_roles_permisos():
    """Respaldar Roles-Permisos"""
    console = Console()
    ruta = Path(ROLES_CSV)
    if ruta.exists():
        console.print(f"[red]ERROR: {ROLES_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    modulos = Modulo.query.order_by(Modulo.id).all()
    console.print("Respaldando roles-permisos...")
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        encabezados = ["rol_id", "nombre"]
        for modulo in modulos:
            encabezados.append(modulo.nombre.lower())
        encabezados.append("estatus")
        respaldo = csv.writer(puntero)
        respaldo.writerow(encabezados)
        for rol in Rol.query.order_by(Rol.id).all():
            renglon = [rol.id, rol.nombre]
            for modulo in modulos:
                permiso_str = ""
                for permiso in rol.permisos:
                    if permiso.modulo_id == modulo.id and permiso.estatus == "A":
                        permiso_str = str(permiso.nivel)
                renglon.append(permiso_str)
            renglon.append(rol.estatus)
            respaldo.writerow(renglon)
            contador += 1
    console.print(f"[green]{contador} roles-permisos respaldados.")


def respaldar_usuarios_roles():
    """Respaldar Usuarios-Roles"""
    console = Console()
    ruta = Path(USUARIOS_ROLES_CSV)
    if ruta.exists():
        console.print(f"[red]ERROR: {USUARIOS_ROLES_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    console.print("Respaldando usuarios-roles...")
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "usuario_id",
                "autoridad_clave",
                "email",
                "nombres",
                "apellido_paterno",
                "apellido_materno",
                "curp",
                "puesto",
                "roles",
                "estatus",
            ]
        )
        for usuario in Usuario.query.order_by(Usuario.id).all():
            roles_list = []
            for usuario_rol in usuario.usuarios_roles:
                if usuario_rol.estatus == "A":
                    roles_list.append(usuario_rol.rol.nombre)
            respaldo.writerow(
                [
                    usuario.id,
                    usuario.autoridad.clave,
                    usuario.email,
                    usuario.nombres,
                    usuario.apellido_paterno,
                    usuario.apellido_materno,
                    usuario.curp,
                    usuario.puesto,
                    ",".join(roles_list),
                    usuario.estatus,
                ]
            )
            contador += 1
    console.print(f"[green]{contador} usuarios-roles respaldados.")


@db.command()
def inicializar():
    """Inicializar la base de datos"""
    console = Console()
    if DEPLOYMENT_ENVIRONMENT != "DEVELOPMENT":
        console.print(f"[red]PROHIBIDO: No se inicializa porque DEPLOYMENT_ENVIRONMENT es {DEPLOYMENT_ENVIRONMENT}.")
        sys.exit(1)
    database.drop_all()
    database.create_all()
    console.print("[green]La base de datos se ha inicializado correctamente.")


@db.command()
def alimentar():
    """Alimentar la base de datos con los datos en los archivos CSV en la carpeta 'seed'"""
    console = Console()
    if DEPLOYMENT_ENVIRONMENT == "PRODUCTION":
        console.print("[red]PROHIBIDO: No se inicializa porque este es el servidor de producción.")
        sys.exit(1)
    alimentar_modulos()
    alimentar_roles()
    alimentar_permisos()
    alimentar_distritos()
    alimentar_autoridades()
    alimentar_usuarios()
    alimentar_usuarios_roles()
    console.print("[green]La base de datos se ha alimentado correctamente.")


@db.command()
def reiniciar():
    """Reiniciar la base de datos (inicializar y alimentar)"""
    inicializar()
    alimentar()


@db.command()
def respaldar():
    """Respaldar la base de datos en archivos CSV"""
    respaldar_autoridades()
    respaldar_distritos()
    respaldar_modulos()
    respaldar_roles_permisos()
    respaldar_usuarios_roles()
