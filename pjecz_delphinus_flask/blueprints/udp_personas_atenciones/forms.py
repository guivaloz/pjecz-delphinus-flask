"""
UDP Personas Atenciones, formularios
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import Length, Optional


class UdpPersonaAtencionForm(FlaskForm):
    """Formulario UdpPersonaAtencion"""

    udp_tipo_tramite = SelectField("Tipo de Trámite", choices=None, validate_choice=False)
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)
    expediente = StringField("Expediente", validators=[Optional(), Length(max=32)])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    guardar = SubmitField("Guardar")
