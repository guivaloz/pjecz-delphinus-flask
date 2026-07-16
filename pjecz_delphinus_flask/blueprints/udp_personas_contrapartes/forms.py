"""
UDP Personas Contrapartes, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class UdpPersonaContraparteForm(FlaskForm):
    """Formulario UdpPersonaContraparte"""

    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_primero = StringField("Apellido Primero", validators=[DataRequired(), Length(max=256)])
    apellido_segundo = StringField("Apellido Segundo", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Length(max=18)])
    nacimiento_fecha = DateField("Fecha de Nacimiento", validators=[Optional()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    guardar = SubmitField("Guardar")
