"""
UDP Tipos Condiciones, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class UdpTipoCondicionForm(FlaskForm):
    """Formulario UdpTipoCondicion"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
