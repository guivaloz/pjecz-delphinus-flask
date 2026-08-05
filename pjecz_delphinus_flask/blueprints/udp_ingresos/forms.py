"""
UDP Ingresos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class UdpIngresoForm(FlaskForm):
    """Formulario UdpIngreso"""

    ocupacion = StringField("Ocupación", validators=[DataRequired(), Length(max=256)])
    ingresos = DecimalField("Ingresos", validators=[DataRequired()], places=2)
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    guardar = SubmitField("Guardar")
