"""
UDP Personas Domicilios, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class UdpPersonaDomicilioForm(FlaskForm):
    """Formulario UdpPersonaDomicilio"""

    estado = SelectField("Estado", validators=[DataRequired()], choices=None, validate_choice=False)
    municipio = SelectField("Municipio", validators=[DataRequired()], choices=None, validate_choice=False)
    calle = StringField("Calle", validators=[DataRequired(), Length(max=256)])
    num_exterior = StringField("Número Exterior", validators=[Optional(), Length(max=64)])
    num_interior = StringField("Número Interior", validators=[Optional(), Length(max=64)])
    colonia = StringField("Colonia", validators=[Optional(), Length(max=256)])
    codigo_postal = IntegerField("Código Postal", validators=[Optional()])
    referencias = TextAreaField("Referencias", validators=[Optional(), Length(max=1024)])
    guardar = SubmitField("Guardar")
