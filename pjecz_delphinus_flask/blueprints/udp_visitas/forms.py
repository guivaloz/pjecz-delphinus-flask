"""
UDP Visitas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class UdpVisitaForm(FlaskForm):
    """Formulario UdpVisita"""

    udp_tipo_visita = SelectField("Tipo de Visita", validators=[DataRequired()], choices=None, validate_choice=False)
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    guardar = SubmitField("Guardar")
