"""
Distritos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from pjecz_delphinus_flask.lib.safe_string import CLAVE_REGEXP


class DistritoForm(FlaskForm):
    """Formulario Distrito"""

    clave = StringField("Clave (única de hasta 16 caracteres)", validators=[DataRequired(), Regexp(CLAVE_REGEXP)])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    nombre_corto = StringField("Nombre corto", validators=[Optional(), Length(max=64)])
    guardar = SubmitField("Guardar")
