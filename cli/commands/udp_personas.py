"""
CLI UDP Personas
"""

import csv
import os
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
from rich.console import Console
from rich.progress import Progress
from typer import Typer

from pjecz_delphinus_flask.app import app
from pjecz_delphinus_flask.blueprints.autoridades.models import Autoridad
from pjecz_delphinus_flask.blueprints.municipios.models import Municipio
from pjecz_delphinus_flask.blueprints.udp_sexos.models import UdpSexo
from pjecz_delphinus_flask.blueprints.udp_tipos_condiciones.models import UdpTipoCondicion
from pjecz_delphinus_flask.blueprints.udp_tipos_tramites.models import UdpTipoTramite
from pjecz_delphinus_flask.blueprints.udp_tipos_visitas.models import UdpTipoVisita
from pjecz_delphinus_flask.blueprints.usuarios.models import Usuario
from pjecz_delphinus_flask.config.extensions import database
from pjecz_delphinus_flask.lib.safe_string import safe_email, safe_string

# Rutas a los archivos CSV
UDP_PERSONAS_CSV = "seed/PERSONAS.csv"

# Inicializar la aplicación
app.app_context().push()

usuarios = Typer()

"""
Columnas del archivo UDP_PERSONAS_CSV:
- ID
- NOMBRE_USUARIO
- FECHA
- NO_EXPEDIENTE
- FECH_NAC_USUARIO
- EDAD
- SEXO
- CONDICIÓN
- NOMBRE_CONTRAPARTE
- FECH_NAC_CONTRAPARTE
- OCUPACIÓN
- INGRESOS
- COLONIA
- TELEFONO
- TRAMITE
- VISITA
- COMO_SE_ENTERO
- OBSERVACIONES
- ATENDIO
- HORA_SALIDA
- ASIGNADO_A
- HORA_SALIDA_AJ
- OBSERVACIONES_AJ
- AÑO_EXPEDIENTE
- FECHA_HORA_EAJ
- CANALIZADO
- FECHA_CANALIZADO
"""
