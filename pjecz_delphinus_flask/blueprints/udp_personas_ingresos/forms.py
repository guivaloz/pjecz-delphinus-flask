"""
UDP Personas Ingresos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField, TextAreaField
from wtforms.validators import Length, Optional


class UdpPersonaIngresoForm(FlaskForm):
    """Formulario UdpPersonaIngreso"""

    ocupacion = StringField("Ocupación", validators=[Optional(), Length(max=256)])
    ingresos = DecimalField("Ingresos", validators=[Optional()], places=2)
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    guardar = SubmitField("Guardar")
