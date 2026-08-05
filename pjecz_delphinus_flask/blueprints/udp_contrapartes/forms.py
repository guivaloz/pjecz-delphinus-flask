"""
UDP Contrapartes, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class UdpContraparteForm(FlaskForm):
    """Formulario UdpContraparte"""

    udp_sexo = SelectField("Sexo", choices=None, validate_choice=False)
    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_primero = StringField("Apellido Primero", validators=[DataRequired(), Length(max=256)])
    apellido_segundo = StringField("Apellido Segundo", validators=[Optional(), Length(max=256)])
    nacimiento_fecha = DateField("Fecha de Nacimiento", validators=[Optional()])
    curp = StringField("CURP", validators=[Optional(), Length(max=18)])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    guardar = SubmitField("Guardar")
